import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    SUMMARY_REQUEST_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)

MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="centered",
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], use_container_width=True)


def add_message(role, kind, content):
    st.session_state.messages.append(
        {"role": role, "kind": kind, "content": content}
    )


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text or "I couldn't generate an explanation for that."
    except Exception as error:
        return f"Sorry, I couldn't process that request: {error}"


def send_email(to_address, subject, body):
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address
    message.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)


def build_summary():
    return ask_gemini([SUMMARY_REQUEST_PROMPT])


# ---------------------------
# Onboarding
# ---------------------------
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Take a picture. Understand it. Save the explanation.")

    st.info(
        "Upload a textbook problem, handwritten note, diagram, code question, "
        "or any study material you want Gemini to explain."
    )

    with st.form("onboarding_form"):
        name = st.text_input("Your name", placeholder="Enter your name")
        email = st.text_input(
            "Email address for summaries",
            placeholder="student@example.com",
        )
        submitted = st.form_submit_button(
            "Start Learning 🚀",
            use_container_width=True,
        )

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please enter both your name and email address.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# ---------------------------
# Main app
# ---------------------------
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📚 Snap & Study")
    st.caption(f"Learning with {st.session_state.name}")

with button_col:
    send_disabled = len(st.session_state.messages) <= 1

    if st.button(
        "📧 Email Summary",
        disabled=send_disabled,
        use_container_width=True,
    ):
        with st.spinner("Preparing your study summary..."):
            summary = build_summary()

        try:
            send_email(
                st.session_state.email,
                "Your Snap & Study Session Summary",
                summary,
            )
            st.success("Summary sent to your email.")
        except Exception as error:
            st.error(f"Couldn't send the email: {error}")


st.caption(f"Summaries will be sent to {st.session_state.email}")

if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )

for message in st.session_state.messages:
    render_message(message)


user_input = st.chat_input(
    "Ask a question, or attach a study image",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text.strip()
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Analyze this study material and explain the important content "
            "in simple language. If it contains a question, solve it step by step."
        )

    with st.spinner("Analyzing your study material..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
    st.rerun()
