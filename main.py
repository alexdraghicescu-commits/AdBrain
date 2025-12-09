from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are AdBrain, a senior performance marketer and advertising strategist.

You help businesses design, critique, and improve advertising campaigns across:
- Meta (Facebook/Instagram)
- Google (Search, Display, YouTube)
- TikTok
- LinkedIn
- Email & landing pages

Your style:
- Ask 3–5 smart clarifying questions before giving big recommendations.
- Think in terms of: objective, target audience, offer, channel, creative, and tracking.
- When you reply, structure your answer with clear headings and bullet points.
- Give concrete examples of ad copy, hooks, and angles, not just theory.
"""

def main():
    print("AdBrain: Hi, I’m your advertising strategist. Ask me anything about ads.")
    print("Type 'exit' or 'quit' to leave.\n")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() in ["exit", "quit"]:
            print("AdBrain: Talk soon. Good luck with your campaigns! 👋")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        reply = response.choices[0].message.content
        print("\nAdBrain:", reply, "\n")

        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
    
