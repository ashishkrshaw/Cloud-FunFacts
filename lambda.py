import json
import boto3
import random
import unicodedata

# --- DynamoDB setup ---
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CloudFacts")

# --- Hardcoded witty cloud facts ---
HARDCODED_FACTS = [
    "AWS Lambda: code runs while servers nap. Magic, right?",
    "Cloud saves IT budgets like Netflix saves binge-watchers.",
    "S3 stores more data than all your old USB drives combined.",
    "EC2 instances are tiny workers tirelessly running your apps.",
    "CloudFront delivers content faster than your morning coffee.",
    "DynamoDB handles requests like a caffeinated squirrel on speed.",
    "Serverless means servers exist, but they work in stealth mode.",
    "AWS regions are like global coffee shops for your data.",
    "Cloud reduces CO2, proving IT can be eco-friendly too.",
    "CloudWatch watches your apps like hawks on espresso shots.",
    "CloudFormation stacks resources faster than a pancake chef.",
    "S3 versioning: because accidents happen, even in the cloud.",
    "Elastic Load Balancer juggles traffic like a circus pro.",
    "Auto Scaling grows apps like Jack’s beanstalk on steroids.",
    "Cloud lets startups go global without selling kidneys first."
]

def to_safe_ascii(text):
    """
    Convert text to pure ASCII:
    - Normalize Unicode characters (’ → ')
    - Remove emojis/symbols
    - Strip newlines/spaces
    """
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.strip()

def lambda_handler(event, context):
    # Try to fetch items from DynamoDB
    try:
        response = table.scan()
        items = response.get("Items", [])
    except Exception:
        items = []

    # Randomly decide whether to use DynamoDB or hardcoded facts
    use_dynamodb = bool(items) and random.random() < 0.5

    if use_dynamodb:
        fact = random.choice(items)["FactText"]
    else:
        fact = random.choice(HARDCODED_FACTS)

    # Sanitize fact text for safe ASCII
    safe_fact = to_safe_ascii(fact)

    # Return clean JSON
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"fact": safe_fact}, ensure_ascii=True)
    }
