#!/usr/bin/env python3
"""
H.A.A — إعداد Telegram Webhook
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
شغّل هذا الملف مرة واحدة لربط بوت التيليجرام بـ GitHub.

الاستخدام:
  python3 scripts/setup_webhook.py

المتطلبات:
  - TELEGRAM_BOT_TOKEN في متغيرات البيئة
  - GH_PAT في متغيرات البيئة
  - GH_REPO (مثال: hussain/HAA)
"""

import os
import sys
import json
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GH_PAT    = os.environ.get("GH_PAT", "")
GH_REPO   = os.environ.get("GH_REPO", "")  # مثال: hussain-ali/HAA

# ────────────────────────────────────────────────────────────────
# تحقق من المتطلبات
# ────────────────────────────────────────────────────────────────
if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN غير موجود")
    sys.exit(1)
if not GH_PAT:
    print("❌ GH_PAT غير موجود")
    sys.exit(1)
if not GH_REPO:
    print("❌ GH_REPO غير موجود (مثال: hussain-ali/HAA)")
    sys.exit(1)

# ────────────────────────────────────────────────────────────────
# جلب معلومات البوت
# ────────────────────────────────────────────────────────────────
print("🤖 التحقق من معلومات البوت...")
me_resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
if me_resp.status_code != 200 or not me_resp.json().get("ok"):
    print(f"❌ توكن البوت غير صحيح: {me_resp.text[:200]}")
    sys.exit(1)

bot_info = me_resp.json()["result"]
print(f"✅ البوت: @{bot_info['username']} ({bot_info['first_name']})")

# ────────────────────────────────────────────────────────────────
# إنشاء Webhook URL
# تستخدم GitHub Pages لاستقبال الطلبات وتحويلها لـ Dispatch
# ────────────────────────────────────────────────────────────────
# ملاحظة: GitHub Actions لا يدعم webhooks مباشرة.
# الحل: استخدام خدمة Cloudflare Worker أو smee.io أو GitHub Pages JS

print("\n" + "=" * 60)
print("📡 إعداد Webhook التيليجرام")
print("=" * 60)
print("""
⚠️  ملاحظة مهمة:
GitHub Actions لا يقبل webhooks خارجية مباشرة.
هناك خيارات للربط:

━━━ الخيار 1: Cloudflare Worker (مجاني - موصى به) ━━━
1. أنشئ حساب Cloudflare Workers المجاني
2. انسخ هذا الكود للـ Worker:

```javascript
export default {
  async fetch(request, env) {
    if (request.method !== 'POST') return new Response('OK');
    const body = await request.json();
    
    await fetch(`https://api.github.com/repos/${env.GH_REPO}/dispatches`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.GH_PAT}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github+json'
      },
      body: JSON.stringify({
        event_type: 'telegram_webhook',
        client_payload: { message: body.message }
      })
    });
    
    return new Response('OK');
  }
};
```

3. أضف في Worker Variables:
   - GH_PAT: توكن GitHub الخاص بك
   - GH_REPO: hussain-ali/HAA

4. سيكون الـ Webhook URL:
   https://your-worker.workers.dev

━━━ الخيار 2: smee.io (للتطوير فقط) ━━━
1. اذهب إلى smee.io وأنشئ قناة جديدة
2. ستحصل على URL مثل: https://smee.io/xxxxx
3. شغّل: npx smee -u https://smee.io/xxxxx

━━━ الخيار 3: الاستخدام اليدوي ━━━
استخدم لوحة التحكم (dashboard/index.html) مباشرة
بدون الحاجة لبوت تيليجرام.
""")

# ────────────────────────────────────────────────────────────────
# اختبار الـ Dispatch
# ────────────────────────────────────────────────────────────────
print("\n🧪 اختبار Repository Dispatch...")
test_resp = requests.post(
    f"https://api.github.com/repos/{GH_REPO}/dispatches",
    headers={
        "Authorization": f"Bearer {GH_PAT}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    },
    json={
        "event_type": "haa_build_request",
        "client_payload": {
            "request": "اختبار: مرحباً من السكريبت الإعدادي",
            "project_name": "haa-test"
        }
    }
)

if test_resp.status_code == 204:
    print("✅ Repository Dispatch يعمل بشكل صحيح!")
    print(f"   تحقق من: https://github.com/{GH_REPO}/actions")
else:
    print(f"❌ فشل الاختبار ({test_resp.status_code}): {test_resp.text[:200]}")
    print("   تأكد من أن GH_PAT لديه صلاحية 'repo' و 'workflow'")

print("\n✅ انتهى الإعداد!")
