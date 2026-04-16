# ⚡ H.A.A — Hussain Ali Automation

<div align="center">

```
  ██╗  ██╗ █████╗  █████╗ 
  ██║  ██║██╔══██╗██╔══██╗
  ███████║███████║███████║
  ██╔══██║██╔══██║██╔══██║
  ██║  ██║██║  ██║██║  ██║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
```

**أداة أتمتة بدون سيرفر — تحوّل أفكارك إلى مشاريع جاهزة**

![GitHub Actions](https://img.shields.io/badge/Engine-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions)
![Claude AI](https://img.shields.io/badge/Brain-Claude_AI-CC785C?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Notify-Telegram-26A5E4?style=for-the-badge&logo=telegram)
![Serverless](https://img.shields.io/badge/Mode-Serverless-00C7B7?style=for-the-badge)

</div>

---

## 🧠 ما هي H.A.A؟

H.A.A هي أداة أتمتة **Serverless** تعمل بالكامل داخل GitHub. ترسل طلباً، يفكر الذكاء الاصطناعي، يُنشأ المشروع، وتستلم الرابط على تيليجرام — بدون أي سيرفر خارجي.

---

## ⚙️ المعمارية

```
[أنت]  →  Issue / Telegram / Dashboard
              ↓
    [GitHub Actions — H.A.A Engine]
              ↓
       [Claude AI — المعالج]
              ↓
   [GitHub API — بناء المستودع]
              ↓
  [Telegram Bot — إشعار + رابط]
```

---

## 🚀 إعداد الأداة (Setup)

### 1. Fork هذا المستودع

### 2. أضف هذه Secrets في `Settings → Secrets → Actions`:

| Secret | الوصف |
|--------|-------|
| `ANTHROPIC_API_KEY` | مفتاح Claude API |
| `GH_PAT` | GitHub Personal Access Token (repo, workflow) |
| `TELEGRAM_BOT_TOKEN` | توكن بوت التيليجرام |
| `TELEGRAM_CHAT_ID` | معرف محادثتك مع البوت |
| `GMAIL_USER` | بريد Gmail (اختياري) |
| `GMAIL_APP_PASSWORD` | App Password لـ Gmail (اختياري) |

### 3. فعّل GitHub Pages من `Settings → Pages → Branch: main → /dashboard`

---

## 📖 طريقة الاستخدام

### الطريقة 1: عبر Issue
افتح Issue جديد في المستودع وضع طلبك في العنوان:
```
[HAA] أريد بوت تيليجرام بلغة Python يرد على الرسائل
```

### الطريقة 2: عبر لوحة التحكم
افتح `dashboard/index.html` المنشورة على GitHub Pages وأرسل طلبك.

### الطريقة 3: عبر تيليجرام
أرسل رسالة للبوت بصيغة:
```
/build أريد API بلغة Python تجلب أسعار العملات
```

---

## 📁 هيكل الملفات

```
HAA/
├── .github/
│   └── workflows/
│       ├── haa-main.yml          # المحرك الرئيسي
│       └── haa-builder.yml       # بناء المشاريع
├── scripts/
│   ├── ai_processor.py           # طبقة الذكاء الاصطناعي
│   ├── github_builder.py         # إنشاء المستودعات
│   └── notifier.py               # الإشعارات
├── config/
│   └── settings.json             # الإعدادات
├── dashboard/
│   └── index.html                # لوحة التحكم
└── README.md
```

---

## 🛡️ الأمان

- جميع المفاتيح تُخزن في GitHub Secrets (مشفرة)
- المستودع الخاص (Private Repo) للحفاظ على الخصوصية
- يمكن تفعيل قائمة بيضاء لعناوين IP عبر Webhook

---

<div align="center">
صُنع بـ ❤️ من Hussain Ali
</div>
