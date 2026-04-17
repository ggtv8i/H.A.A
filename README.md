# ⚡ H.A.A Flow

محرك أتمتة بصري مثل n8n — بنودات تعمل **فعلاً** مع Claude AI، Telegram، GitHub، HTTP وأكثر.

---

## 🚀 التشغيل السريع

```bash
# 1. استنسخ المشروع
git clone https://github.com/YOUR_USERNAME/haa-flow.git
cd haa-flow

# 2. ثبّت الحزم
npm install

# 3. أعدّ المتغيرات
cp .env.example .env
# ثم افتح .env وأضف مفاتيحك

# 4. شغّل السيرفر
npm start
# أو للتطوير مع إعادة التشغيل التلقائي:
npm run dev
```

افتح المتصفح على: **http://localhost:3000**

---

## 📋 متطلبات التشغيل

- Node.js **18+**
- حسابات API اختيارية (Claude، OpenAI، Telegram، GitHub، Gmail)

---

## 🧩 النودات المتاحة

### ⚡ محفزات
| النود | الوظيفة |
|-------|---------|
| **Webhook** | يستقبل طلبات HTTP حقيقية من أي خدمة |
| **جدول زمني** | تشغيل تلقائي بـ Cron Expression |
| **Telegram In** | استقبال رسائل Telegram Bot |
| **GitHub Event** | استقبال أحداث GitHub Webhook |

### 🧠 ذكاء اصطناعي
| النود | الوظيفة |
|-------|---------|
| **Claude AI** | استدعاء Anthropic API حقيقي |
| **OpenAI** | استدعاء OpenAI API حقيقي |
| **تصنيف نص** | تصنيف النصوص بـ Claude أو قواعد بسيطة |

### ⚙️ منطق
| النود | الوظيفة |
|-------|---------|
| **If** | تفرع منطقي حقيقي بشروط |
| **Switch** | تفرع متعدد |
| **Loop** | تكرار على مصفوفة |
| **Merge** | دمج مدخلين |
| **Wait** | تأخير التنفيذ |

### 📡 إجراءات
| النود | الوظيفة |
|-------|---------|
| **Telegram Send** | إرسال رسائل Telegram حقيقية |
| **HTTP Request** | طلبات HTTP/REST حقيقية |
| **GitHub API** | استدعاء GitHub REST API |
| **Email** | إرسال Gmail |
| **كود JS** | تنفيذ JavaScript مباشرة |

### 💾 بيانات
| النود | الوظيفة |
|-------|---------|
| **Set Data** | تعيين قيم ثابتة |
| **Filter** | فلترة المصفوفات |
| **Transform** | تحويل البيانات بقوالب |
| **Debug** | طباعة البيانات للتصحيح |

---

## 🔧 إعداد المتغيرات (.env)

```env
PORT=3000

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
OPENAI_API_KEY=sk-...

# Telegram Bot
TELEGRAM_BOT_TOKEN=

# GitHub
GITHUB_TOKEN=

# Email (Gmail App Password)
EMAIL_USER=your@gmail.com
EMAIL_PASS=your-app-password
```

---

## 🌐 Webhook الخارجي

لتشغيل Workflow عبر HTTP من خدمة خارجية:

```
POST http://YOUR_SERVER/api/webhooks/{WORKFLOW_ID}
```

مثال مع Telegram:
1. في BotFather، اضبط الـ Webhook:
   ```
   https://api.telegram.org/bot{TOKEN}/setWebhook?url=http://YOUR_SERVER/api/webhooks/{WORKFLOW_ID}
   ```

---

## 📁 هيكل المشروع

```
haa-flow/
├── server.js                    # السيرفر الرئيسي
├── src/
│   ├── engine/
│   │   ├── executor.js          # محرك التنفيذ + WebSocket
│   │   └── nodeExecutors.js     # تنفيذ كل نود
│   ├── routes/
│   │   ├── workflows.js         # API لإدارة الـ Workflows
│   │   └── webhooks.js          # نقاط التشغيل الخارجي
│   └── storage/
│       └── fileStorage.js       # حفظ الـ Workflows كـ JSON
├── public/
│   └── index.html               # واجهة المستخدم
└── workflows/                   # مجلد الـ Workflows المحفوظة (مُنشأ تلقائياً)
```

---

## 🎮 اختصارات لوحة المفاتيح

| المفتاح | الوظيفة |
|---------|---------|
| `F` | ملاءمة جميع النودات |
| `Delete` | حذف النود المحدد |
| `Ctrl+S` | حفظ الـ Workflow |
| `Esc` | إلغاء التحديد |

---

## 🔌 API Reference

```
GET    /api/workflows         # قائمة الـ Workflows
POST   /api/workflows         # إنشاء Workflow
GET    /api/workflows/:id     # جلب Workflow
PUT    /api/workflows/:id     # تحديث Workflow
DELETE /api/workflows/:id     # حذف Workflow

POST   /api/webhooks/:id      # تشغيل Workflow خارجياً

GET    /api/health            # فحص حالة السيرفر

WS     /ws                    # WebSocket للتنفيذ الحقيقي
```

---

## 🚀 النشر على الإنترنت

### Railway
```bash
railway login
railway init
railway up
```

### Render
1. ارفع المشروع على GitHub
2. أنشئ Web Service جديد على render.com
3. أضف متغيرات البيئة
4. انتشر!

---

## 📄 الرخصة

MIT © H.A.A
