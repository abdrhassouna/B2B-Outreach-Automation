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

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_16_digit_app_password" 
PDF_PATH = r"C:\Path\To\Your\portfolio.pdf"
SENDER_NAME = "Your Name"

LEADS_FILE = "leads.csv"
EMAIL_TRACKER_FILE = "email_contacted_leads.csv"
WP_TRACKER_FILE = "wp_contacted_leads.csv"
BATCH_SIZE = 25  # Safe daily limit for free Gmail accounts

if not os.path.exists(LEADS_FILE):
    print(f"Error: {LEADS_FILE} not found.")
    exit()

df_leads = pd.read_csv(LEADS_FILE, dtype={'phone': str})

# 1. Identify companies already emailed
email_contacted_names = set()
if os.path.exists(EMAIL_TRACKER_FILE):
    try:
        df_email_done = pd.read_csv(EMAIL_TRACKER_FILE)
        email_contacted_names = set(df_email_done['company_name'].dropna().astype(str).str.strip().str.lower())
    except Exception:
        email_contacted_names = set()

# 2. Target leads that haven't been emailed yet
pending_emails = df_leads[~df_leads['company_name'].astype(str).str.strip().str.lower().isin(email_contacted_names)]

if pending_emails.empty:
    print("No pending leads ready for email outreach right now.")
    exit()

batch_to_email = pending_emails.head(BATCH_SIZE)
print(f"Starting Email batch: {len(batch_to_email)} leads queued.")

def send_pitch(to_email, contact_name, company_name):
    msg = MIMEMultipart()
    msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = f"Custom Services for {company_name}"

    body = f"""Hi {contact_name},

[Your email pitch goes here. Keep it concise and personalized to {company_name}.]

Best regards,
{SENDER_NAME}
"""
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(PDF_PATH):
        with open(PDF_PATH, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename="Case_Study.pdf")
            msg.attach(attach)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

for index, row in batch_to_email.iterrows():
    company = row['company_name'] if pd.notna(row.get('company_name')) else "your company"
    contact = row['contact_name'] if pd.notna(row.get('contact_name')) else "there"
    raw_email = row.get('email')

    if pd.notna(raw_email) and "@" in str(raw_email):
        clean_email = str(raw_email).strip().split(';')[0].strip()
        try:
            send_pitch(clean_email, contact, company)
            print(f"Sent email to {clean_email} ({company})")
            
            # Safe SMTP cooldown timer (60-120s to prevent velocity locks)
            cooldown = random.randint(60, 120)
            print(f"Waiting {cooldown}s before next email...")
            time.sleep(cooldown)
            
        except Exception as e:
            print(f"Failed sending email to {clean_email}: {e}")
    else:
        print(f"No valid email listed for {company}, skipping email send.")

    # Immediately log this lead to email_contacted_leads.csv
    logged_row = pd.DataFrame([row])
    header_needed = not os.path.exists(EMAIL_TRACKER_FILE)
    
    # SAFETY CHECK: Ensure the file ends with a clean new line before appending
    if not header_needed:
        with open(EMAIL_TRACKER_FILE, "a+", encoding="utf-8") as f:
            f.seek(0, 2)
            if f.tell() > 0:
                f.seek(f.tell() - 1, 0)
                if f.read(1) != '\n':
                    f.write('\n')

    logged_row.to_csv(EMAIL_TRACKER_FILE, mode='a', header=header_needed, index=False)

# 4. Smart Cleanup: Remove fully processed leads
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

print(f"\nEmail sequence finished successfully!")
print(f"{len(remaining_leads)} leads remaining in {LEADS_FILE} awaiting further processing.")