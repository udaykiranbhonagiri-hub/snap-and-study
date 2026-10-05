Snap & Study
AI study assistant using Streamlit, Gemini Vision, and Gmail.
Gemini API version
This version uses the Gemini Interactions API with the stable
`gemini-3.8-flash` model and `previous_interaction_id` for multi-turn
conversation state.
Run locally
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example`,
then:
```bash
python -m streamlit run app.py
```
Secrets
```toml
GEMINI_API_KEY = "your-real-gemini-api-key"
GMAIL_ADDRESS = "your-gmail@gmail.com"
GMAIL_APP_PASSWORD = "your-gmail-app-password"
```
Never commit `.streamlit/secrets.toml`.
Flow
Image/text -> Gemini Vision + Chat -> explanation -> conversation -> Gemini
revision summary -> Gmail SMTP -> student's email.