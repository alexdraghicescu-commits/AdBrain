import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Local: load from .env
load_dotenv()

# Try Streamlit secrets first (for cloud), fall back to env var (for local)
api_key = None
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

BASE_SYSTEM_PROMPT = """
You are AdBrain, a senior performance marketer and advertising strategist.

You help businesses design, critique, and improve advertising campaigns across:
- Meta (Facebook/Instagram)
- Google (Search, Display, YouTube)
- TikTok
- LinkedIn
- Email & landing pages

General behavior:
- Always ask 3–5 smart clarifying questions before giving big recommendations.
- Think in terms of: objective, target audience, offer, channel, creative, and tracking.
- When you reply, structure your answer with clear headings and bullet points.
- Give concrete examples of ad copy, hooks, and angles, not just theory.
- End with a short 'Action plan for today' section.
"""

MODE_PROMPTS = {
    "Campaign Strategy": """
Current mode: CAMPAIGN STRATEGY.

Focus on:
- Choosing the right channels
- Budget allocation
- Funnel structure (awareness / consideration / conversion)
- High-level messaging angles

Output:
- Campaign overview
- Channel mix and rationale
- Example messages per channel
""",
    "Copywriting": """
Current mode: COPYWRITING.

Focus on:
- Hooks, headlines, primary text, CTAs
- Platform-specific best practices (Meta, TikTok, Google, etc.)
- Multiple variations for testing

Output:
- 3–5 strong hooks
- 3–5 ad copy variations
- Suggested CTAs
""",
    "Ad Audit": """
Current mode: AD AUDIT.

The user will paste existing ads (text, sometimes rough creative description).

Focus on:
- Diagnosing what's working / not working
- Messaging clarity, offer strength, and relevance
- Providing concrete improvement suggestions and rewrites

Output:
- Quick diagnosis
- Bullet-point improvements
- Rewritten, stronger versions of the ad
""",
    "Persona / Offer Builder": """
Current mode: PERSONA / OFFER BUILDER.

Focus on:
- Clarifying target audience
- Pain points, desires, objections
- Refining the core offer and positioning

Output:
- 1–2 detailed personas
- Key pains and desires
- Offer positioning and messaging angles
"""
}


def build_system_prompt(mode_name: str) -> str:
    extra = MODE_PROMPTS.get(mode_name, "")
    return BASE_SYSTEM_PROMPT + "\n" + extra


st.set_page_config(page_title="AdBrain – Ad Strategist", layout="centered")

st.title("🧠 AdBrain – Advertising Strategist")
st.write("Talk to a senior performance marketer about your campaigns, offers, and ideas.")

# Sidebar: mode selection
mode = st.sidebar.radio(
    "Mode",
    ["Campaign Strategy", "Copywriting", "Ad Audit", "Persona / Offer Builder"],
)

st.sidebar.markdown("### How to use")
st.sidebar.write(
    "Describe your business, offer, audience, and goal.\n\n"
    "AdBrain will ask clarifying questions and then recommend angles, copy, and strategy."
)

# Initialize session state
if "mode" not in st.session_state:
    st.session_state["mode"] = mode

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Reset conversation if mode changes
if mode != st.session_state["mode"]:
    st.session_state["mode"] = mode
    st.session_state["messages"] = []

    # Add fresh system prompt for new mode
    system_prompt = build_system_prompt(mode)
    st.session_state["messages"].append({"role": "system", "content": system_prompt})

# Ensure we at least have a system prompt
if not st.session_state["messages"]:
    system_prompt = build_system_prompt(mode)
    st.session_state["messages"].append({"role": "system", "content": system_prompt})

# Render chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask AdBrain about your advertising…")

if user_input:
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state["messages"],
        )
        reply = response.choices[0].message.content

        # Show assistant reply
        with st.chat_message("assistant"):
            st.markdown(reply)

        # Save assistant message
        st.session_state["messages"].append(
            {"role": "assistant", "content": reply}
        )

    except Exception as e:
        with st.chat_message("assistant"):
            st.markdown(f"⚠️ Error talking to the model:\n\n`{e}`\n\nCheck your API key / quota.")
