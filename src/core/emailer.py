import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List, Dict

def send_job_email(jobs: List[Dict], subject: str = None):
    """
    Sends an aggregated email of high-scoring job matches using Gmail SMTP.
    """
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_APP_PASSWORD")
    email_to = os.getenv("EMAIL_TO")
    
    if not email_user or not email_password or not email_to:
        print("Error: Email credentials or recipient not set in .env")
        return

    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_to
    msg['Subject'] = subject or f"Top {len(jobs)} Job Matches for Your Profile"

    html_content = f"""
    <html>
    <body>
        <h2>Top Job Matches Found</h2>
        <p>The AI Agent has found {len(jobs)} jobs that match your profile (Score 7/10 or higher).</p>
        <hr>
    """

    for job in jobs:
        eval_data = job.get('evaluation', {})
        html_content += f"""
        <div style="margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px;">
            <h3 style="color: #2e7d32;">[{job.get('score')}/10] {job.get('title')}</h3>
            <p><strong>Company:</strong> {job.get('company')}</p>
            <p><strong>Reasoning:</strong> {eval_data.get('reasoning')}</p>
            <p><strong>Highlights:</strong> {', '.join(eval_data.get('match_highlights', []))}</p>
            <p><a href="{job.get('link')}" style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">View & Apply</a></p>
        </div>
        """

    html_content += """
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))

    # Send the email via Gmail SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_password)
            server.send_message(msg)
            print(f"Email successfully sent to {email_to}")
    except Exception as e:
        print(f"Failed to send email: {e}")
