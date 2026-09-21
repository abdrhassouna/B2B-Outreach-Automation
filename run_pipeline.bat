@echo off
echo =========================================
echo 🚀 STARTING B2B OUTREACH PIPELINE
echo =========================================

echo.
echo Activating Virtual Environment...
call venv\Scripts\activate

echo.
echo [1/2] Launching WhatsApp...
python send_whatsapp.py

echo.
echo [2/2] Launching Emails...
python send_emails.py

echo.
echo =========================================
echo ✅ FULL PIPELINE FINISHED!
echo =========================================
pause