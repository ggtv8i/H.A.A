#!/usr/bin/env python3
"""
H.A.A — AI Processor
━━━━━━━━━━━━━━━━━━━━
يتصل بـ Claude API لتحليل الطلب وتوليد هيكل المشروع الكامل.
النتيجة: ملف project_manifest.json يحتوي على جميع ملفات المشروع.
"""

import os
import json
import sys
import re
import anthropic

# ─── الإعدادات ────────────────────────────────────────────────────
API_KEY      = os.environ.get("ANTHROPIC_API_KEY", "")
REQUEST_TEXT = os.environ.get("REQUEST_TEXT", "")
PROJECT_NAME = os.environ.get("PROJECT_NAME", "haa-project")
MODEL        = "claude-opus-4-5"
MAX_TOKENS   = 8000

SYSTEM_PROMPT = """أنت مهندس برمجيات خبير متخصص في بناء مشاريع كاملة وجاهزة للإنتاج.
مهمتك: تحليل طلب المستخدم وتوليد هيكل مشروع كامل.

القواعد الصارمة:
1. أجب دائماً بـ JSON فقط — لا نص، لا شرح، لا ```json``` فقط الـ JSON الخام
2. اجعل الكود واقعياً وقابلاً للتشغيل فعلاً
3. أضف تعليقات واضحة بالعربية داخل الكود
4. كل ملف يجب أن يكون مكتملاً وصالحاً للاستخدام

صيغة الإجابة (JSON):
{
  "project_name": "اسم المشروع",
  "description": "وصف قصير للمشروع",
  "language": "لغة البرمجة الرئيسية",
  "type": "نوع المشروع (bot/api/web/cli/etc)",
  "files": [
    {
      "path": "مسار الملف",
      "content": "محتوى الملف الكامل"
    }
  ],
  "setup_steps": ["خطوة 1", "خطوة 2"],
  "dependencies": ["اعتماد1", "اعتماد2"],
  "env_vars": [
    {"key": "VAR_NAME", "description": "وصف المتغير", "required": true}
  ],
  "features": ["ميزة 1", "ميزة 2"]
}"""


def generate_project(request: str, project_name: str) -> dict:
    """يستدعي Claude API ويعيد manifest المشروع."""
    client = anthropic.Anthropic(api_key=API_KEY)

    user_message = f"""ابنِ مشروعاً كاملاً بناءً على هذا الطلب:

الطلب: {request}
اسم المشروع المقترح: {project_name}

تأكد من تضمين:
- ملف README.md شامل ومفصل
- ملف .gitignore مناسب
- ملف requirements.txt أو package.json (حسب اللغة)
- الكود الرئيسي المكتمل والقابل للتشغيل
- ملف .env.example مع جميع المتغيرات المطلوبة
- أي ملفات إضافية ضرورية للمشروع"""

    print(f"🤖 إرسال الطلب إلى Claude: {request[:80]}...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()

    # تنظيف أي wrapping غير مرغوب
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    try:
        manifest = json.loads(raw)
        print(f"✅ تم توليد المشروع: {len(manifest.get('files', []))} ملف")
        return manifest
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في تحليل JSON: {e}")
        print(f"الرد الخام:\n{raw[:500]}")
        sys.exit(1)


def validate_manifest(manifest: dict) -> bool:
    """التحقق من صحة بنية الـ manifest."""
    required_keys = ["files", "description"]
    for key in required_keys:
        if key not in manifest:
            print(f"⚠️ الـ manifest ناقص: مفتاح '{key}' غير موجود")
            return False

    if not manifest["files"]:
        print("⚠️ لا توجد ملفات في المشروع")
        return False

    for i, file in enumerate(manifest["files"]):
        if "path" not in file or "content" not in file:
            print(f"⚠️ ملف #{i} ناقص: يجب أن يحتوي على 'path' و 'content'")
            return False

    return True


def save_manifest(manifest: dict, output_path: str = "/tmp/project_manifest.json"):
    """حفظ الـ manifest للاستخدام في الخطوة التالية."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"💾 تم حفظ الـ manifest: {output_path}")


def set_github_env(key: str, value: str):
    """تعيين متغير بيئة لـ GitHub Actions."""
    env_file = os.environ.get("GITHUB_ENV", "")
    if env_file:
        with open(env_file, "a") as f:
            f.write(f"{key}={value}\n")


def main():
    if not API_KEY:
        print("❌ ANTHROPIC_API_KEY غير موجود في Secrets")
        sys.exit(1)

    if not REQUEST_TEXT:
        print("❌ REQUEST_TEXT فارغ")
        sys.exit(1)

    print("=" * 60)
    print("⚡ H.A.A — AI Processor")
    print("=" * 60)
    print(f"📝 الطلب: {REQUEST_TEXT}")
    print(f"📦 المشروع: {PROJECT_NAME}")
    print("-" * 60)

    # توليد المشروع
    manifest = generate_project(REQUEST_TEXT, PROJECT_NAME)

    # التحقق من الصحة
    if not validate_manifest(manifest):
        sys.exit(1)

    # تحديث اسم المشروع من الـ manifest إذا كان أفضل
    if "project_name" in manifest and manifest["project_name"]:
        clean_name = re.sub(r'[^a-zA-Z0-9\-_]', '-', manifest["project_name"]).lower()
        clean_name = re.sub(r'-+', '-', clean_name).strip('-')[:50]
        if clean_name:
            set_github_env("PROJECT_NAME", clean_name)
            print(f"📛 اسم المشروع المحدث: {clean_name}")

    # حفظ الـ manifest
    save_manifest(manifest)

    # طباعة ملخص
    print("\n📊 ملخص المشروع المولّد:")
    print(f"  • الوصف: {manifest.get('description', 'N/A')}")
    print(f"  • اللغة: {manifest.get('language', 'N/A')}")
    print(f"  • النوع: {manifest.get('type', 'N/A')}")
    print(f"  • الملفات: {len(manifest.get('files', []))}")
    print(f"  • الميزات: {len(manifest.get('features', []))}")

    if manifest.get("files"):
        print("\n📁 الملفات:")
        for f in manifest["files"]:
            size = len(f.get("content", ""))
            print(f"    {f['path']} ({size} حرف)")

    print("\n✅ AI Processor اكتمل بنجاح!")


if __name__ == "__main__":
    main()
