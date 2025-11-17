1. How It All Started

I started the FunFact Generator project with one simple goal:
to improve my real hands-on cloud skills and understand how AWS services work in an actual application, not just in theory.

As a fresher learning AWS by myself, I often felt confused about how services connect, how frontend talks to backend, and how to deploy real projects. I wanted to build something small but meaningful — something that shows my ability to build an end-to-end cloud solution.

That is how the journey of this project began.

2. What I Wanted to Learn

I wanted a project that forced me to explore:

AWS Amplify Hosting

S3 buckets for static sites

API Gateway routing

CORS problems (and real solutions)

Lambda functions

DynamoDB database operations

IAM permissions

Amazon Bedrock (AI) integration

As someone who is learning by myself, I didn’t have a teacher or mentor.
I learned everything by doing, failing, fixing, and repeating.

3. Choosing the Project Idea

I wanted something simple and fun — not too corporate, but still technical.

So I chose:
➡ A FunFact Generator that shows random facts
➡ Enhances them using AI to make them witty
➡ Displays them instantly on the webpage

It’s a small idea, but it touches almost every major part of serverless cloud development.

4. The Confusion Phase (Real Struggles)
4.1. Understanding Amplify

At first, I didn’t understand how Amplify works:

Does it use CloudFront?

Does it upload to S3?

Do I manage CloudFront myself?

I learned that Amplify handles everything internally, and I only need to upload my index.html and deploy.

This cleared a major confusion for me.

4.2. CORS Errors

My frontend was calling API Gateway, and everything broke because of CORS.

I spent hours debugging:

Why is the API blocked?

Why does the browser reject the response?

Why do I need OPTIONS?

Finally, I understood how CORS works
→ Different domains
→ Browser security
→ API Gateway allowing origin
→ Lambda sending correct headers

This was one of the biggest learning points in this project.

4.3. IAM Role Struggles

Lambda was failing because:

It could not read DynamoDB

It could not call Amazon Bedrock

I learned how to attach IAM permissions, how to use policies, and why least privilege matters.
This experience taught me secure and correct access control.

5. Building the Backend

Once the frontend was deployed and CORS fixed, I worked on the backend.

Lambda Function

Fetches random fact from DynamoDB

Calls Amazon Bedrock to rewrite the fact into a witty/funny style

Returns the response back to API Gateway

DynamoDB

I stored random facts in a simple table with keys like:

id (number)
fact (string)

API Gateway

Integrated with Lambda to act as the middle point between frontend and backend.

6. Adding AI (Amazon Bedrock)

This was the most exciting part.

I used Bedrock to take a normal fact like:

"Honey never spoils."

And turn it into something witty:

"Honey never spoils — just like your love for procrastinating."

Learning how to call Bedrock from Lambda made me understand:

Model invocation

Request/response format

Token usage

Error handling

It gave my project a unique touch — showing I can integrate AI into real apps.

7. Understanding the Architecture (My Turning Point)

After a lot of trial and error, I finally understood the full architecture clearly:

User → Amplify → S3 → JS → API Gateway → Lambda → DynamoDB → Bedrock → Response


This understanding improved my confidence the most.
For the first time, I felt like I could build actual cloud applications, not just follow tutorials.

8. What I Learned (My Real Takeaways)
✔ How cloud services communicate
✔ How frontend interacts with backend
✔ How to create and deploy APIs
✔ How serverless architecture works
✔ How to debug cloud issues
✔ How IAM permissions work
✔ How to use AI (Bedrock) in backend workflows
✔ How to independently build and fix problems

This project didn’t just teach me AWS —
it taught me problem solving and patience.

9. How This Project Changed Me

This was more than a technical project.
It boosted my confidence as an aspiring cloud engineer.

Before this project:

I was unsure about AWS

I feared CORS errors

I didn’t understand architectures

After this project:

I can design end-to-end architectures

I can fix issues independently

I can integrate multiple AWS services

I can deploy real applications

I can explain technical systems professionally

This project made me feel like a real developer, not just a learner.

10. My Future Plans

Add login/authentication

Add "Fact Analytics" to track user clicks

Add multi-language fact generation

Improve UI

Use DynamoDB streams for auto-updates

Create a mobile version using Flutter

11. Final Reflection

This project represents my:

Curiosity

Self-learning ability

Persistence

Desire to become a cloud engineer

Love for building real things

Even though I’m a fresher, this project shows that I can:

Build

Debug

Deploy

Document

Think in architecture

Integrate AI

And most importantly — learn anything by myself.
