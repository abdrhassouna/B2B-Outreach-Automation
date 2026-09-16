import os
import time
import random
import pandas as pd
import pywhatkit as kit
import phonenumbers
import pyautogui

LEADS_FILE = "leads.csv"
WP_TRACKER_FILE = "wp_contacted_leads.csv"
BATCH_SIZE = 50

def format_international_phone(raw_phone, country_code="US"):
    if not raw_phone or pd.isna(raw_phone):
        return None
    raw_str = str(raw_phone).strip()
    try:
        parsed = phonenumbers.parse(raw_str, country_code)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return None
    except phonenumbers.NumberParseException:
        return None

if not os.path.exists(LEADS_FILE):
    print(f"Error: {LEADS_FILE} not found.")
    exit()

df_leads = pd.read_csv(LEADS_FILE, dtype={'phone': str})

contacted_companies = set()
if os.path.exists(WP_TRACKER_FILE):
    try:
        df_wp_done = pd.read_csv(WP_TRACKER_FILE)
        contacted_companies = set(df_wp_done['company_name'].dropna().astype(str).str.strip().str.lower())
    except Exception:
        contacted_companies = set()

pending_leads = df_leads[~df_leads['company_name'].astype(str).str.strip().str.lower().isin(contacted_companies)]

if pending_leads.empty:
    print("No pending leads left for WhatsApp outreach!")
    exit()

daily_batch = pending_leads.head(BATCH_SIZE)
print(f"Starting WhatsApp batch: {len(daily_batch)} leads.")

for index, row in daily_batch.iterrows():
    company = row['company_name'] if pd.notna(row.get('company_name')) else "your company"
    name = row['contact_name'] if pd.notna(row.get('contact_name')) else "there"
    raw_phone = row.get('phone')
    csv_country = str(row.get('country', 'US')).strip().upper()
    region = "US" if csv_country == "USA" else csv_country

    phone = format_international_phone(raw_phone, country_code=region)

    if not phone:
        print(f"Skipping invalid/missing phone for {company}: {raw_phone}")
    else:
        message = (
            f"Hi {name}, I am reaching out on behalf of 2 architects - Ahmed ElRifaie and Ahmed Ghorab - "
            f"that have noticed the work {company} is doing across the region.\n\n"
            "We develop custom AI visual systems for pool companies—replacing generic "
            "stock photos with hyper-realistic imagery of your branded uniforms, service trucks, "
            "and specific equipment pads, and even planning construction!\n\n"
            "If you are interested to know more, it would be our uttermost pleasure to schedule a meeting with you!\n\n"
            "You can view our short Cabana Pools case study here, along with other projects in different fields:\n"
            "https://drive.google.com/drive/folders/12vDL3I90akwldwZdxKOmU6MXR5jomwq-?usp=sharing"
        )

        try:
            print(f"Sending WhatsApp to {name} at {company} ({phone})...")
            kit.sendwhatmsg_instantly(phone_no=phone, message=message, wait_time=20, tab_close=False)
            
            time.sleep(8)
            pyautogui.click()
            pyautogui.press('enter')
            
            print(f"Delivered WhatsApp message to {company} ({phone})")
            
            time.sleep(3)
            pyautogui.hotkey('ctrl', 'w')
            
            cooldown = random.randint(20, 40)
            print(f"Cooldown: waiting {cooldown}s...")
            time.sleep(cooldown)
            
        except Exception as e:
            print(f"Error sending WhatsApp to {phone}: {e}")

    logged_row = pd.DataFrame([row])
    header_needed = not os.path.exists(WP_TRACKER_FILE)
    logged_row.to_csv(WP_TRACKER_FILE, mode='a', header=header_needed, index=False)

print(f"\nWhatsApp batch complete! All {len(daily_batch)} leads logged to {WP_TRACKER_FILE}.")
print("Next step: Run 'python send_emails.py' to finish the sequence.")