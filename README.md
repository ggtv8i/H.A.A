# ⚡ H.A.A Flow

<div align="center">

**محرك أتمتة بصري — مثل n8n — يعمل بالكامل في المتصفح**

[![GitHub Pages](https://img.shields.io/badge/Live-GitHub_Pages-00C7B7?style=for-the-badge&logo=github)](https://YOUR_USERNAME.github.io/haa-flow)
[![HTML](https://img.shields.io/badge/Pure-HTML%2FJS-E34F26?style=for-the-badge&logo=html5)](index.html)
[![No Server](https://img.shields.io/badge/Mode-No_Server-2088FF?style=for-the-badge)](.)

</div>

---

## 🎯 ما هو H.A.A Flow؟

محرر Workflow بصري يعمل في المتصفح مباشرةً — بدون سيرفر، بدون تثبيت.  
اسحب النودات، اربطها، وشغّل الـ Workflow.

## 🔗 الرابط المباشر

بعد الرفع على GitHub Pages:
```
https://YOUR_USERNAME.github.io/haa-flow
```

---

## 🚀 الرفع على GitHub (خطوتان)

### الخطوة 1 — ارفع المستودع
```bash
git init
git add .
git commit -m "🚀 أول إصدار من H.A.A Flow"
git remote add origin https://github.com/YOUR_USERNAME/haa-flow.git
git push -u origin main
```

### الخطوة 2 — فعّل GitHub Pages
1. اذهب إلى **Settings** → **Pages**
2. في **Source** اختر: **GitHub Actions**
3. احفظ ← سيُنشر الموقع تلقائياً ✅

> الـ Workflow الموجود في `.github/workflows/deploy.yml` يتولى كل شيء.

---

## ✨ الميزات

| الميزة | التفاصيل |
|--------|----------|
| 🖱️ سحب وإفلات | اسحب النودات من الشريط الجانبي |
| 🔗 ربط بصري | خطوط Bezier تربط المنافذ |
| 🤖 22 نود جاهز | Webhook، Claude AI، Telegram، GitHub، HTTP... |
| ▶ تشغيل محاكي | تشغيل فعلي مع سجل نشاط |
| 🎨 4 قوالب | بوت تيليجرام، AI Pipeline، GitHub Auto، جلب بيانات |
| 💾 تصدير JSON | حفظ الـ Workflow ملف JSON |
| 🗺️ Minimap | خريطة مصغرة للـ Canvas |

---

## 📁 هيكل الملفات

```
haa-flow/
├── index.html               ← التطبيق الكامل
├── README.md
├── .nojekyll                ← يمنع Jekyll من معالجة الملفات
└── .github/
    └── workflows/
        └── deploy.yml       ← نشر تلقائي على GitHub Pages
```

---

<div align="center">صُنع بـ ❤️ من Hussain Ali</div>
