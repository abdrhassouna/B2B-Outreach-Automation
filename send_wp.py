"""
WINDOWS SETUP & EXECUTION:
1. Ensure your CSV files (leads.csv) are in the same folder as this script.
2. Open Command Prompt (cmd).
3. Navigate to your project directory (e.g., cd E:\Projects\POOL_OUTREACH)
4. Run the script: python send_whatsapp.py
5. CRITICAL: Immediately move your physical mouse to the empty top title bar 
   of your browser and leave it there. This forces Windows to keep the browser 
   in focus so the 'Enter' keystroke registers correctly.
"""

import os
import time
import random
import pandas as pd
import pywhatkit as kit
import phonenumbers
import pyautogui

# --- [PLACEHOLDER VALUES BELOW] ---
LEADS_FILE = "dummy_leads.csv" # Placeholder for your master leads list
WP_TRACKER_FILE = "wp_contacted_leads.csv" 
BATCH_SIZE = 50 
# --- [END PLACEHOLDERS] ---

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
        print(f"Skipping invalid phone for {company}")
    else:
        # --- [PLACEHOLDER VALUE]: Customize your pitch below ---
        message = f"Hi {name}, I am reaching out to see if {company} needs custom AI visuals..."
        
        try:
            kit.sendwhatmsg_instantly(phone_no=phone, message=message, wait_time=20, tab_close=False)
            time.sleep(8)
            pyautogui.click() # Clicks current mouse position to grab window focus
            pyautogui.press('enter')
            
            time.sleep(3)
            pyautogui.hotkey('ctrl', 'w') # Closes browser tab
            
            # Anti-ban cooldown timer
            time.sleep(random.randint(20, 40)) 
            
        except Exception as e:
            print(f"Error sending to {phone}: {e}")

    # Immediately log this lead to wp_contacted_leads.csv
        logged_row = pd.DataFrame([row])
        header_needed = not os.path.exists(WP_TRACKER_FILE)
        
        # SAFETY CHECK: Ensure the file ends with a clean new line before appending
        if not header_needed:
            with open(WP_TRACKER_FILE, "a+", encoding="utf-8") as f:
                f.seek(0, 2)
                if f.tell() > 0:
                    f.seek(f.tell() - 1, 0)
                    if f.read(1) != '\n':
                        f.write('\n')
    
        logged_row.to_csv(WP_TRACKER_FILE, mode='a', header=header_needed, index=False)

print(f"\nWhatsApp batch complete! All {len(daily_batch)} leads logged to {WP_TRACKER_FILE}.")
print("Next step: Run 'python send_emails.py' to finish the sequence.")