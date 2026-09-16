"""
WINDOWS SETUP & EXECUTION:
1. Ensure your PDF attachment and CSV files are in the same directory.
2. Open Command Prompt (cmd).
3. Navigate to your project directory.
4. Run the script: python send_emails.py
5. This script runs via background SMTP, so you can minimize the terminal.
"""

import os
import smtplib
import time
import random
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# --- [PLACEHOLDER VALUES BELOW] ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your_email@gmail.com" # [PLACEHOLDER VALUE]
APP_PASSWORD = "your_app_password" # [PLACEHOLDER VALUE] Do not share your real password!
PDF_PATH = r"C:\Path\To\Your\dummy_portfolio.pdf" # [PLACEHOLDER VALUE]

LEADS_FILE = "dummy_leads.csv" # [PLACEHOLDER VALUE]
EMAIL_TRACKER_FILE = "email_contacted_leads.csv"
WP_TRACKER_FILE = "wp_contacted_leads.csv"
BATCH_SIZE = 25 # Lower limit to protect SMTP reputation
# --- [END PLACEHOLDERS] ---

if not os.path.exists(LEADS_FILE):
    print("Leads file not found.")
    exit()

df_leads = pd.read_csv(LEADS_FILE, dtype={'phone': str})

email_contacted_names = set()
if os.path.exists(EMAIL_TRACKER_FILE):
    try:
        df_email_done = pd.read_csv(EMAIL_TRACKER_FILE)
        email_contacted_names = set(df_email_done['company_name'].dropna().astype(str).str.strip().str.lower())
    except Exception:
        pass

pending_emails = df_leads[~df_leads['company_name'].astype(str).str.strip().str.lower().isin(email_contacted_names)]

if pending_emails.empty:
    exit()

batch_to_email = pending_emails.head(BATCH_SIZE)

def send_pitch(to_email, contact_name, company_name):
    msg = MIMEMultipart()
    msg['From'] = f"Your Name <{SENDER_EMAIL}>" # [PLACEHOLDER VALUE]
    msg['To'] = to_email
    msg['Subject'] = f"Custom Request for {company_name}" # [PLACEHOLDER VALUE]

    # [PLACEHOLDER VALUE] customize body text
    body = f"Hi {contact_name},\n\nThis is a placeholder pitch for {company_name}."
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(PDF_PATH):
        with open(PDF_PATH, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename="portfolio.pdf")
            msg.attach(attach)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

for index, row in batch_to_email.iterrows():
    company = row['company_name'] if pd.notna(row.get('company_name')) else "Company"
    contact = row['contact_name'] if pd.notna(row.get('contact_name')) else "there"
    raw_email = row.get('email')

    if pd.notna(raw_email) and "@" in str(raw_email):
        clean_email = str(raw_email).strip().split(';')[0].strip()
        try:
            send_pitch(clean_email, contact, company)
            time.sleep(random.randint(180, 300)) # 3 to 5 minute SMTP cooldown
        except Exception as e:
            pass

    logged_row = pd.DataFrame([row])
    header_needed = not os.path.exists(EMAIL_TRACKER_FILE)
    logged_row.to_csv(EMAIL_TRACKER_FILE, mode='a', header=header_needed, index=False)

# Smart Cleanup Logic
df_email_done = pd.read_csv(EMAIL_TRACKER_FILE)
em_set = set(df_email_done['company_name'].dropna().astype(str).str.strip().str.lower())

wp_set = set()
if os.path.exists(WP_TRACKER_FILE):
    try:
        df_wp_done = pd.read_csv(WP_TRACKER_FILE)
        wp_set = set(df_wp_done['company_name'].dropna().astype(str).str.strip().str.lower())
    except Exception:
        pass

fully_processed_companies = em_set.intersection(wp_set)
remaining_leads = df_leads[~df_leads['company_name'].astype(str).str.strip().str.lower().isin(fully_processed_companies)]
remaining_leads.to_csv(LEADS_FILE, index=False)