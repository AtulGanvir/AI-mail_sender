import streamlit as st
import smtplib
from email.message import EmailMessage
from openai import OpenAI

st.title("AI-Powered Email Sender App")

# Sidebar API Key
api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")

# Initialize client
client = None
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

def generate_email_content(prompt):
    """Generate email content using AI"""
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are a helpful email writing assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Error generating content: {e}")
        return None


# Email inputs
sender = st.text_input("Your Gmail address")
password = st.text_input("Gmail App Password", type="password")
recipient = st.text_input("Recipient Email")

# Email context
email_context = st.text_area(
    "What is this email about?",
    placeholder="Example: Write a professional email to schedule a meeting with a client next week"
)

# Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Generate Subject"):
        if not api_key:
            st.error("Please enter OpenRouter API key")
        elif email_context:
            with st.spinner("Generating subject..."):
                prompt = f"Generate a short professional email subject line for: {email_context}"
                subject = generate_email_content(prompt)

                if subject:
                    st.session_state["generated_subject"] = subject
                    st.success("Subject generated!")

with col2:
    if st.button("Generate Message"):
        if not api_key:
            st.error("Please enter OpenRouter API key")
        elif email_context:
            with st.spinner("Generating message..."):
                prompt = f"Write a professional email body for: {email_context}"
                message_content = generate_email_content(prompt)

                if message_content:
                    st.session_state["generated_message"] = message_content
                    st.success("Message generated!")


# Generated fields
subject = st.text_input(
    "Subject",
    value=st.session_state.get("generated_subject", "")
)

message = st.text_area(
    "Message",
    value=st.session_state.get("generated_message", ""),
    height=300
)


# Send email
if st.button("Send Email"):

    if not sender or not password or not recipient or not subject or not message:
        st.warning("Please fill all fields.")

    else:
        try:
            msg = EmailMessage()
            msg["From"] = sender
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.set_content(message)

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)

            st.success("Email sent successfully!")

        except smtplib.SMTPAuthenticationError:
            st.error("Authentication failed. Check your Gmail App Password.")

        except smtplib.SMTPException as e:
            st.error(f"SMTP error occurred: {e}")

        except Exception as e:
            st.error(f"Unexpected error: {e}")