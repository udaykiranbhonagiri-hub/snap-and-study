📚 Snap & Study
Snap & Study is a Streamlit AI study assistant built with Gemini Vision.
A student can upload a photo of a textbook problem, handwritten notes,
diagram, mathematical question, programming question, or other study
material. Gemini analyzes the image and explains it in simple language.
When the session is complete, the student can click Email Summary to
generate a revision summary and send it to their email through Gmail SMTP.
Features
- 📷 Image-based study assistance
- 💬 Conversational Gemini chat
- 🧠 Step-by-step explanations
- 📝 Support for notes, diagrams, math, and code questions
- 📧 Email the complete study-session summary
- 🔐 API keys stored with Streamlit secrets
- ☁️ Ready for Streamlit Community Cloud
Project structure
snap-and-study/
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
Requirements
- Python 3.9+
- Google AI Studio Gemini API key
- Gmail account with 2-Step Verification enabled
- Gmail App Password
Local setup
1. Clone the repository
git clone YOUR_GITHUB_REPOSITORY_URL
cd snap-and-study
2. Create a virtual environment
Windows:
python -m venv venv
venv\Scripts\activate
macOS/Linux:
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure secrets
Copy:
.streamlit/secrets.toml.example
to:
.streamlit/secrets.toml
Then add your real values:
GEMINI_API_KEY = "your-real-key"
GMAIL_ADDRESS = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-gmail-app-password"
Never commit .streamlit/secrets.toml to GitHub.
5. Run the app
streamlit run app.py
Open the local URL shown by Streamlit, normally:
http://localhost:8501
Gmail App Password setup
Do not put your normal Gmail password in the application.
Use:
1. Enable 2-Step Verification on your Google account.
2. Open your Google Account security settings.
3. Create an App Password.
4. Put the generated 16-character password in GMAIL_APP_PASSWORD.
Streamlit Community Cloud deployment
1. Push this project to a public GitHub repository.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select the GitHub repository.
5. Select app.py as the main file.
6. Open the app's Secrets settings.
7. Paste your real secrets in TOML format.
8. Deploy.
The GitHub repository should contain secrets.toml.example, but never
the real secrets.toml.
Core flow
Student
   ↓
Upload image / type question
   ↓
Streamlit
   ↓
Gemini Vision + Chat
   ↓
Study explanation
   ↓
Conversation history
   ↓
Email Summary
   ↓
Gemini creates revision summary
   ↓
Gmail SMTP
   ↓
Student's email
Why this project fits the assignment
The project follows the same building blocks as the workshop reference:
- Streamlit interface
- Gemini chat and vision
- Separate prompts.py
- One-time onboarding
- Persistent chat session using Streamlit session state
- Image + text input
- A single action button
- AI-generated conversation summary
- External delivery through an action tool
The domain is changed from nutrition to education, making the project a
distinct student application rather than a copy of MacroSnap.
Security
Never commit:
.streamlit/secrets.toml
The repository only tracks:
.streamlit/secrets.toml.example