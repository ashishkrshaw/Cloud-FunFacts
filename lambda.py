import boto3
import random
import json
import urllib3
import os
import traceback
import hashlib
from typing import Optional, Tuple
import unicodedata

# DynamoDB connection
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CloudFacts")

# Perplexity API settings
# NOTE: You asked to hardcode the API key. Storing secrets in source is insecure.
# Replace the placeholder below with your real Perplexity API key if you want it hardcoded.
LLM_API_URL = "https://api.perplexity.ai/chat/completions"
# Hardcoded API key placeholder - replace with your key if you really want it in source
LLM_API_KEY = "your Key"

# Initialize urllib3 PoolManager
http = urllib3.PoolManager()

def call_llm_api(fact: str, style: str) -> str:
    """
    Call Perplexity API to make the fact witty/funny using urllib3.
    """
    # If no API key is configured (or left as placeholder), fall back to a local witty transformer so the app still responds nicely.
    if not LLM_API_KEY or LLM_API_KEY.startswith('PUT_'):
        print("No valid API key, using local fallback.")
        return local_fallback_witty(fact, style)

    # Decide randomly: 70% chance to rephrase the input fact, 30% chance to generate a new cloud computing fun fact
    generate_new = random.random() < 0.3  # 30% chance for new fact

    print(f"Calling Perplexity API with fact: '{fact}' and style: '{style}' - Mode: {'Generate New' if generate_new else 'Rephrase'}")

    if generate_new:
        prompt = (
            f"Generate a new, original cloud computing fun fact in the {style} style. "
            "Make it concise (1-2 sentences), clever, witty, and sarcastic. Use puns, unexpected metaphors, or dry humor. "
            "Keep it family-friendly and return only the fact string without surrounding quotes or explanations."
        )
    else:
        prompt = (
            f"Rewrite the following cloud computing fact in the {style} style as a concise (1-2 sentence), clever, witty, and sarcastic line. "
            "Use puns, unexpected metaphors, or dry humor, keep it family-friendly, and do not add any extra explanation or disclaimers. "
            "Return only the rewritten fact string without surrounding quotes.\n\n"
            f"Fact: {fact}"
        )

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        # Some LLM endpoints accept a temperature-like parameter; include if supported by your API.
        "temperature": 0.8
    }

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        r = http.request(
            "POST",
            LLM_API_URL,
            body=json.dumps(payload),
            headers=headers,
            timeout=15
        )
        print(f"API response status: {r.status}")
        data = json.loads(r.data.decode("utf-8"))
        print(f"API response data: {data}")

        # Robust parsing — different LLMs/bridges return slightly different shapes.
        witty_fact = None
        if isinstance(data, dict):
            # Common pattern: {'choices': [{'message': {'content': '...'}}]}
            witty_fact = (
                data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", None)
            )
            # Older/alternate shapes: {'choices': [{'text': '...'}]}
            if not witty_fact:
                witty_fact = data.get("choices", [{}])[0].get("text")

        if witty_fact:
            print(f"Extracted witty fact: '{witty_fact.strip()}'")
            return witty_fact.strip()
        else:
            print("Perplexity API returned no content, using original fact.")
            return fact
    except Exception:
        print("Perplexity API error:\n", traceback.format_exc())
        return local_fallback_witty(fact, style)


def local_fallback_witty(fact: str, style: Optional[str] = None) -> str:
    """
    Create a lightweight witty transformation locally when the LLM is unavailable.
    This keeps the UX playful without any external calls.
    """
    templates = {
        'sarcastic': [
            "{fact} — and people still act surprised.",
            "{fact} Yep, that happened. You're welcome.",
            "{fact} Because who needs simplicity?",
            "{fact} Plot twist: it's actually useful.",
        ],
        'dry': [
            "{fact} In summary: predictable, but useful.",
            "{fact} Not glamorous, just reliable.",
            "{fact} Facts are stubborn things.",
            "{fact} Efficiency at its finest.",
        ],
        'punny': [
            "{fact} Cloud computing: where the servers get their silver linings.",
            "{fact} It's not magic, it's just well-placed electrons.",
            "{fact} Data in the cloud: floating on a sea of sarcasm.",
            "{fact} Servers: the unsung heroes of the digital age.",
        ],
        'self-deprecating': [
            "{fact} We tried explaining it and now the cloud is offended.",
            "{fact} I'm just a function trying my best.",
            "{fact} Even the cloud has better jokes.",
            "{fact} My code is as reliable as this fact.",
        ],
        'playful': [
            "{fact} That's the cloud doing a little dance.",
            "{fact} Imagine tiny servers sipping coffee together.",
            "{fact} Clouds: fluffy on the outside, powerful within.",
            "{fact} Data storage with a side of whimsy.",
        ],
        'default': [
            "{fact} — basically, the cloud's version of a swiss army knife.",
            "{fact} In short: clouds do more than just look fluffy.",
            "{fact} Cloud magic in action.",
            "{fact} Because local storage is so last century.",
        ]
    }

    low = fact.lower()
    if "server" in low:
        chosen = "{fact} — servers: where the clouds do their heavy lifting."
    elif "data" in low:
        chosen = "{fact} — proof that data has commitment issues: it lives everywhere."
    else:
        style_key = (style or 'default').lower()
        candidates = templates.get(style_key, templates['default'])
        chosen = random.choice(candidates)

    witty = chosen.format(fact=fact)
    # Keep it short
    if len(witty) > 200:
        witty = witty[:197].rstrip() + "..."
    return witty


def compute_fact_id(fact_text: str) -> str:
    """Compute a short deterministic id for a fact using SHA1 hex (first 12 chars)."""
    h = hashlib.sha1(fact_text.encode('utf-8')).hexdigest()
    return h[:12]


def read_metadata(metadata_table_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Read last served fact id and last style from metadata table. Returns (last_fact_id, last_style).
    If the table or item doesn't exist, returns (None, None).
    """
    try:
        meta_table = dynamodb.Table(metadata_table_name)
        resp = meta_table.get_item(Key={'PK': 'METADATA'})
        item = resp.get('Item')
        if not item:
            return None, None
        return item.get('LastFactId'), item.get('LastStyle')
    except Exception:
        # Table might not exist or no permissions — silently ignore and fallback
        return None, None


def write_metadata(metadata_table_name: str, last_fact_id: Optional[str], last_style: Optional[str]) -> None:
    """Write last served fact id and style into metadata table. Creates/overwrites the METADATA item.
    Fails silently if table isn't available.
    """
    try:
        meta_table = dynamodb.Table(metadata_table_name)
        meta_table.put_item(Item={
            'PK': 'METADATA',
            'LastFactId': last_fact_id,
            'LastStyle': last_style
        })
    except Exception:
        return

def lambda_handler(event, context):

    # Fetch all facts from DynamoDB (with clear error reporting)
    try:
        response = table.scan()
    except Exception as e:
        print("DynamoDB scan error:\n", traceback.format_exc())
        return {
            "statusCode": 502,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "DynamoDBError", "message": str(e)})
        }

    items = response.get("Items", [])
    if not items:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"fact": "No facts available in DynamoDB."})
        }

    # Pick a random fact and validate its shape
    item = random.choice(items)
    fact = item.get("FactText")
    if not fact:
        print("DynamoDB item missing 'FactText':", item)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "InvalidItem", "message": "DynamoDB item missing 'FactText'"})
        }

    # Determine style selection: rotate or random. Use METADATA_TABLE if configured to avoid repeats.
    metadata_table = os.environ.get('METADATA_TABLE')
    last_fact_id, last_style = (None, None)
    if metadata_table:
        last_fact_id, last_style = read_metadata(metadata_table)

    # Choose a style that is different from last_style when possible
    styles = ['sarcastic', 'dry', 'punny', 'self-deprecating', 'playful']
    chosen_style = random.choice(styles)
    if last_style in styles and len(styles) > 1 and last_style == chosen_style:
        # pick a different one
        alternatives = [s for s in styles if s != last_style]
        chosen_style = random.choice(alternatives)

    # Call Perplexity API to make it witty
    try:
        witty_fact = call_llm_api(fact, chosen_style)
    except Exception as e:
        # call_llm_api already handles fallbacks, but guard here too
        print("LLM call error:\n", traceback.format_exc())
        return {
            "statusCode": 502,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "LLMError", "message": str(e)})
        }

    # Ensure the returned string contains only ASCII characters to avoid unicode/emoji mixing
    witty_fact = sanitize_to_ascii(witty_fact)

    print(f"Final witty fact after sanitization: '{witty_fact}'")

    # Save metadata to avoid immediate repeats (best-effort)
    if metadata_table:
        try:
            write_metadata(metadata_table, compute_fact_id(fact), chosen_style)
        except Exception:
            print("Failed to write metadata (non-fatal):\n", traceback.format_exc())

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({"fact": witty_fact})
    }


def sanitize_to_ascii(text: str) -> str:
    """
    Remove non-ASCII characters from text by normalizing and stripping anything that can't be
    encoded as ASCII. This removes emojis and other Unicode characters so the output is plain ASCII.
    """
    if text is None:
        return text
    # First replace common Unicode punctuation with ASCII equivalents so they are preserved
    replacements = {
        '\u2019': "'",  # right single quote (curly apostrophe)
        '\u2018': "'",  # left single quote
        '\u2014': '-',    # em dash
        '\u2013': '-',    # en dash
        '\u2012': '-',    # figure dash
        '\u2010': '-',    # hyphen
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2026': '...',  # ellipsis
    }
 
    for uni, ascii_eq in replacements.items():
        text = text.replace(uni, ascii_eq)

    # Normalize to decompose combined characters, then drop other non-ascii bytes
    normalized = unicodedata.normalize('NFKD', text)
    ascii_bytes = normalized.encode('ascii', 'ignore')
    return ascii_bytes.decode('ascii')
