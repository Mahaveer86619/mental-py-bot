import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def create_email_template(user_name, condition, severity, recommendations):
    """
    Creates an HTML email template for emergency contact.

    Args:
        user_name (str): The user's name or username.
        condition (str): The mental health condition assessed.
        severity (str): The severity result.
        recommendations (list): List of recommendations for the recipient.

    Returns:
        str: The HTML email template as a string.
    """
    recommendations_html = "".join(f"<li>{rec}</li>" for rec in recommendations)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MindGuide AI - Emergency Alert</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                overflow: hidden;
            }}
            .header {{
                background: #dc3545;
                color: #fff;
                padding: 24px 32px;
                text-align: center;
            }}
            .content {{
                padding: 32px;
            }}
            .result-section {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 24px;
                border-left: 6px solid #2575fc;
            }}
            .result-label {{
                font-weight: bold;
                color: #2575fc;
            }}
            .severity {{
                font-size: 1.2em;
                font-weight: bold;
                color: #dc3545;
                margin-bottom: 10px;
            }}
            .recommendations {{
                margin-top: 20px;
                background: #e9f7ef;
                border-radius: 8px;
                padding: 18px;
            }}
            .recommendations h3 {{
                margin-top: 0;
                color: #218838;
            }}
            .footer {{
                background: #f2f2f2;
                color: #888;
                text-align: center;
                font-size: 0.95em;
                padding: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Emergency Alert from MindGuide AI</h1>
            </div>
            <div class="content">
                <p>Dear Emergency Contact,</p>
                <p>
                    <b>{user_name}</b> has completed a mental health assessment using MindGuide AI.
                    The results indicate the following:
                </p>
                <div class="result-section">
                    <div><span class="result-label">Condition:</span> {condition}</div>
                    <div class="severity">Severity: {severity}</div>
                </div>
                <div class="recommendations">
                    <h3>Recommended Actions for You</h3>
                    <ul>
                        {recommendations_html}
                    </ul>
                </div>
                <p>
                    Please reach out to <b>{user_name}</b> as soon as possible to provide support and care.
                    If you believe they are in immediate danger, contact emergency services.
                </p>
                <p>
                    <i>This message was sent automatically by MindGuide AI for the safety and well-being of its users.</i>
                </p>
            </div>
            <div class="footer">
                Sent on: {datetime.now().strftime("%B %d, %Y %H:%M")}
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_email(subject, sender_email, receiver_email, html_content):
    """
    Sends an HTML email.

    Args:
        subject (str): The subject of the email.
        sender_email (str): The sender's email address.
        receiver_email (str): The recipient's email address.
        html_content (str): The HTML content of the email.
    """
    password = os.getenv("APP_PASSWORD")

    # Create message container
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn HTML into plain/html MIMEText objects
    part = MIMEText(html_content, "html")

    # Add HTML part to MIMEMultipart message
    message.attach(part)

    # Create secure connection with server and send email
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    # Example usage
    sender_email = "mahaveer86619.dev@gmail.com"
    receiver_email = "psatyam86619@gmail.com"
    subject = "Emergency Alert - MindGuide AI"
    user_name = "John Doe"
    condition = "Anxiety"
    severity = "High"
    recommendations = [
        "Contact John immediately to check on his well-being.",
        "Encourage John to seek professional help.",
        "Provide emotional support and listen to his concerns.",
    ]
    html_template = create_email_template(
        user_name, condition, severity, recommendations
    )
    send_email(subject, sender_email, receiver_email, html_template)
