import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def create_email_template(company_name="Your Company", team_name="The Team"):
    """
    Creates an HTML email template.

    Args:
        company_name (str, optional): The name of the company. Defaults to "Your Company".
        team_name (str, optional): The name of the team sending the email. Defaults to "The Team".

    Returns:
        str: The HTML email template as a string.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Monthly Newsletter</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4285f4;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
                background-color: #ffffff;
            }}
            .footer {{
                background-color: #f2f2f2;
                padding: 10px;
                text-align: center;
                font-size: 12px;
                color: #777777;
            }}
            .button {{
                display: inline-block;
                background-color: #4285f4;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            h1, h2 {{
                color: #333333;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{company_name} Newsletter</h1>
                <p>May 2025 Edition</p>
            </div>
            <div class="content">
                <h2>Hello from Our Team!</h2>
                <p>We hope this email finds you well. Here are our latest updates:</p>
                
                <h3>What's New</h3>
                <ul>
                    <li>New product launch coming next month</li>
                    <li>Our team expanded with 5 new members</li>
                    <li>Office relocation scheduled for June</li>
                </ul>
                
                <p>We're excited to share that our Q1 results exceeded expectations with a 15% growth in revenue.</p>
                
                <a href="https://www.example.com/details" class="button">Read More</a>
                
                <p>Thank you for your continued support!</p>
                <p>Best regards,<br>{team_name}</p>
            </div>
            <div class="footer">
                <p>© 2025 {company_name}. All rights reserved.</p>
                <p>You're receiving this email because you subscribed to our newsletter.</p>
                <p><a href="https://www.example.com/unsubscribe">Unsubscribe</a></p>
                <p>Sent on: {datetime.now().strftime("%B %d, %Y")}</p>
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
    subject = "Monthly Newsletter - May 2025"
    html_template = create_email_template()
    send_email(subject, sender_email, receiver_email, html_template)
