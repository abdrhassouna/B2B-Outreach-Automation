# Multi-Channel B2B Outreach Automation

## Overview

A Python-based growth engineering pipeline designed to automate multi-channel B2B sales outreach. This system intelligently handles both GUI-based WhatsApp messaging and backend SMTP email delivery while utilizing dynamic CSV trackers to prevent duplicate contacts and manage daily rate limits.

## Architecture

The pipeline utilizes a batch orchestrator to manage sequential execution within a virtual environment:

1. **`run_pipeline.bat`** : The master orchestrator that activates the virtual environment and triggers the sequential workflow (WhatsApp followed immediately by Email).
2. **`send_wp.py`** : Utilizes `pywhatkit` and `pyautogui` for GUI automation. It reads from a master `leads.csv`, handles OS window-focus bypasses for reliable keystroke injection, and securely logs processed leads.
3. **`send_email.py`** : A backend SMTP script that targets remaining leads. It respects Gmail's strict anti-spam algorithms by utilizing randomized 60-to-120-second cooldown timers to avoid velocity locks.

*Feature Highlight:* Smart dataset intersection logic runs post-execution to compare `email_contacted_leads.csv` and `wp_contacted_leads.csv`, intelligently cleaning the master `leads.csv` queue. The system includes robust file-handling checks to prevent CSV formatting corruption from trailing commas or missing newlines.

## Tech Stack

* **Language:** Python 3
* **Libraries:** `pandas`, `pyautogui`, `pywhatkit`, `phonenumbers`, `smtplib`
* **Data Handling:** Dynamic CSV batching, intersection logic, and automated formatting safeties.

## Author

AbdelRahman Hassouna
