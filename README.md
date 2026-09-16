# Multi-Channel B2B Outreach Automation

## Overview
A Python-based growth engineering pipeline designed to automate multi-channel B2B sales outreach. This system intelligently handles both GUI-based WhatsApp messaging and backend SMTP email delivery while utilizing dynamic CSV trackers to prevent duplicate contacts and manage daily rate limits.

## Architecture
The pipeline is decoupled into two independent scripts:
1. **`send_whatsapp.py`**: Utilizes `pywhatkit` and `pyautogui` for GUI automation. It reads from a master `leads.csv`, handles OS window-focus bypasses for reliable keystroke injection, and logs processed leads.
2. **`send_emails.py`**: An asynchronous SMTP background script that targets remaining leads. It respects Gmail's strict anti-spam algorithms by utilizing randomized 3-to-5-minute cooldown timers and smart dataset intersection to clean the master queue.

## Tech Stack
* **Language:** Python 3
* **Libraries:** `pandas`, `pyautogui`, `pywhatkit`, `phonenumbers`, `smtplib`
* **Data Handling:** Dynamic CSV batching and intersection logic.

## Author
**AbdelRahman Hassouna**
