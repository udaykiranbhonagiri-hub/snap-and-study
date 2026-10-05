import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

import streamlit as st
from google import genai

from prompts import SYSTEM_PROMPT, SUMMARY_REQUEST_PROMPT, WELCOME_MESSAGE_TEMPLATE

MODEL_NAME = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]

st.set_page_config(page_title="Snap & Study", page_icon="📚", layout="centered")

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


def ask_gemini(text, image_bytes=None, mime_type=None, update_history=True):
    if image_bytes is not None:
        input_content = [
            {
                "type": "text",
                "text": text,
            },
            {
                "type": "image",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
                "mime_type": mime_type or "image/jpeg",
            },
        ]
    else:
        input_content = text

    previous_id = st.session_state.get("last_interaction_id")

    last_error = None

    for model_name in MODEL_NAME:
        for attempt in range(3):
            try:
                request_args = {
                    "model": model_name,
                    "input": input_content,
                    "system_instruction": SYSTEM_PROMPT,
                }

                if previous_id:
                    request_args["previous_interaction_id"] = previous_id

                interaction = gemini_client.interactions.create(
                    **request_args
                )

                if update_history:
                    st.session_state.last_interaction_id = interaction.id

                return interaction.output_text or (
                    "I couldn't generate an explanation."
                )

            except Exception as error:
                last_error = error
                error_text = str(error)

                # Retry temporary 503/429 errors.
                if "503" in error_text or "429" in error_text:
                    time.sleep(2 ** attempt)
                    continue

                # Other errors should not be hidden.
                break

    return (
        "Gemini is temporarily unavailable. "
        "Please try again in a moment.\n\n"
        f"Technical detail: {last_error}"
    )


def build_summary():
    try:
        previous_id = st.session_state.get("last_interaction_id")
        if not previous_id:
            return "No study conversation is available yet."

        interaction = gemini_client.interactions.create(
            model=MODEL_NAME,
            input=SUMMARY_REQUEST_PROMPT,
            previous_interaction_id=previous_id,
            system_instruction=SYSTEM_PROMPT,
        )
        return interaction.output_text or "No summary was generated."

    except Exception as error:
        return f"Unable to create summary: {error}"


def send_email(to_address, subject, body):
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address
    message.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)


if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Take a picture. Understand it. Save the explanation.")

    st.info(
        "Upload a textbook problem, handwritten note, diagram, code question, "
        "or study material you want Gemini to explain."
    )

    with st.form("onboarding_form"):
        name = st.text_input("Your name", placeholder="Enter your name")
        email = st.text_input(
            "Email address for summaries",
            placeholder="student@example.com",
        )
        submitted = st.form_submit_button(
            "Start Learning 🚀", use_container_width=True
        )

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please enter both your name and email address.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()
            st.session_state.messages = []
            st.session_state.last_interaction_id = None
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📚 Snap & Study")
    st.caption(f"Learning with {st.session_state.name}")

with button_col:
    send_disabled = st.session_state.get("last_interaction_id") is None

    if st.button("📧 Email Summary", disabled=send_disabled, use_container_width=True):
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

    if not text and photo is None:
        st.warning("Enter a question or attach an image.")
        st.stop()

    photo_bytes = None
    photo_mime = None

    if photo is not None:
        photo_bytes = photo.getvalue()
        photo_mime = photo.type
        add_message("user", "image", photo_bytes)

    if text:
        add_message("user", "text", text)

    prompt = text or (
        "Analyze this study material carefully. Explain what it contains "
        "in simple language. If it contains a question, solve it step by step. "
        "If it contains code, explain the logic and complexity."
    )

    with st.spinner("Analyzing your study material..."):
        answer = ask_gemini(
            prompt,
            image_bytes=photo_bytes,
            mime_type=photo_mime,
        )

    add_message("assistant", "text", answer)
    st.rerun()
