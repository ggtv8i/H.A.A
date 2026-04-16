#!/usr/bin/env python3
"""
H.A.A — Notifier
━━━━━━━━━━━━━━━━
يرسل إشعارات عبر Telegram (وGmail اختيارياً) بعد اكتمال البناء.
"""

import os
import sys
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─── الإعدادات ────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID    = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_CHAT_ID_TG = os.environ.get("TELEGRAM_CHAT_ID_OVERRIDE", "")  # من payload التيليجرام

GMAIL_USER     = os.environ.get("GMAIL_USER", "")
GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

REPO_URL      = os.environ.get("CREATED_REPO_URL", "")
REPO_NAME     = os.environ.get("CREATED_REPO_NAME", "")
PROJECT_NAME  = os.environ.get("PROJECT_NAME", "")
REQUEST_TEXT  = os.environ.get("REQUEST_TEXT", "")
BUILD_STATUS  = os.environ.get("BUILD_STATUS", "success")
GH_RUN_URL    = os.environ.get("GITHUB_SERVER_URL", "https://github.com") + "/" + \
                os.environ.get("GITHUB_REPOSITORY", "") + "/actions/runs/" + \
                os.environ.get("GITHUB_RUN_ID", "")


def send_telegram(chat_id: str, message: str, parse_mode: str = "Markdown") -> bool:
    """إرسال رسالة تيليجرام."""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print("⚠️ تيليجرام: بيانات غير مكتملة، تخطي...")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }, timeout=15)

    if resp.status_code == 200:
        print("✅ تم إرسال إشعار التيليجرام")
        return True
    else:
        print(f"⚠️ فشل إرسال تيليجرام ({resp.status_code}): {resp.text[:200]}")
        return False


def build_telegram_success_message() -> str:
    """بناء رسالة نجاح التيليجرام."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""⚡ *H.A.A — مشروعك جاهز!*

✅ *تم بناء المشروع بنجاح*
━━━━━━━━━━━━━━━━━━━━

📝 *الطلب:*
{REQUEST_TEXT or 'غير محدد'}

📦 *اسم المشروع:*
`{REPO_NAME or PROJECT_NAME or 'haa-project'}`

🔗 *رابط المستودع:*
{REPO_URL or 'غير متاح'}

⏰ *الوقت:* {now}

━━━━━━━━━━━━━━━━━━━━
🤖 _Powered by H.A.A Engine_"""


def build_telegram_failure_message() -> str:
    """بناء رسالة فشل التيليجرام."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""⚡ *H.A.A — تقرير البناء*

❌ *حدث خطأ أثناء البناء*
━━━━━━━━━━━━━━━━━━━━

📝 *الطلب:*
{REQUEST_TEXT or 'غير محدد'}

🔍 *تفاصيل الخطأ:*
[عرض سجلات الـ Workflow]({GH_RUN_URL})

⏰ *الوقت:* {now}

━━━━━━━━━━━━━━━━━━━━
💡 تحقق من إعدادات الـ Secrets وأعد المحاولة.
🤖 _Powered by H.A.A Engine_"""


def send_gmail_notification():
    """إرسال إشعار بريد إلكتروني عبر Gmail (اختياري)."""
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("ℹ️ Gmail: بيانات غير موجودة، تخطي...")
        return

    status_ar   = "✅ نجح" if BUILD_STATUS == "success" else "❌ فشل"
    subject     = f"H.A.A — {status_ar} — {PROJECT_NAME or 'مشروع جديد'}"

    html_body = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #161b22; border-radius: 12px; overflow: hidden; border: 1px solid #30363d; }}
    .header {{ background: linear-gradient(135deg, #1f6feb, #388bfd); padding: 30px; text-align: center; }}
    .header h1 {{ margin: 0; color: #fff; font-size: 28px; letter-spacing: 2px; }}
    .header p {{ margin: 8px 0 0; color: rgba(255,255,255,0.8); }}
    .body {{ padding: 30px; }}
    .status {{ text-align: center; font-size: 48px; margin: 20px 0; }}
    .info-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #30363d; }}
    .info-label {{ color: #8b949e; font-size: 14px; }}
    .info-value {{ color: #c9d1d9; font-weight: bold; font-size: 14px; }}
    .btn {{ display: block; width: fit-content; margin: 24px auto; padding: 14px 32px; background: #238636; color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; }}
    .footer {{ background: #0d1117; padding: 16px; text-align: center; color: #8b949e; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>⚡ H.A.A</h1>
      <p>Hussain Ali Automation Engine</p>
    </div>
    <div class="body">
      <div class="status">{'✅' if BUILD_STATUS == 'success' else '❌'}</div>
      <h2 style="text-align:center; color: {'#3fb950' if BUILD_STATUS == 'success' else '#f85149'}">
        {'تم بناء مشروعك بنجاح!' if BUILD_STATUS == 'success' else 'حدث خطأ أثناء البناء'}
      </h2>
      <div class="info-row">
        <span class="info-label">الطلب</span>
        <span class="info-value">{(REQUEST_TEXT or 'غير محدد')[:60]}</span>
      </div>
      <div class="info-row">
        <span class="info-label">اسم المشروع</span>
        <span class="info-value">{REPO_NAME or PROJECT_NAME or 'haa-project'}</span>
      </div>
      <div class="info-row">
        <span class="info-label">الحالة</span>
        <span class="info-value">{status_ar}</span>
      </div>
      {'<a class="btn" href="' + REPO_URL + '">🔗 فتح المستودع</a>' if REPO_URL else ''}
    </div>
    <div class="footer">تم الإرسال بواسطة H.A.A Engine · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
  </div>
</body>
</html>"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = GMAIL_USER
        msg["To"]      = GMAIL_USER

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)

        print("✅ تم إرسال إشعار Gmail")
    except Exception as e:
        print(f"⚠️ فشل إرسال Gmail: {e}")


def main():
    print("=" * 60)
    print("📨 H.A.A — Notifier")
    print("=" * 60)
    print(f"📊 الحالة: {BUILD_STATUS}")
    print(f"🔗 الرابط: {REPO_URL or 'N/A'}")

    # تحديد الـ Chat ID (أولوية للـ override من تيليجرام)
    chat_id = TELEGRAM_CHAT_ID_TG or TELEGRAM_CHAT_ID

    # إرسال تيليجرام
    if BUILD_STATUS == "success":
        msg = build_telegram_success_message()
    else:
        msg = build_telegram_failure_message()

    send_telegram(chat_id, msg)

    # إرسال Gmail (اختياري)
    send_gmail_notification()

    print("\n✅ Notifier اكتمل!")


if __name__ == "__main__":
    main()
