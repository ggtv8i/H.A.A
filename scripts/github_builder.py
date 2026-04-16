#!/usr/bin/env python3
"""
H.A.A — GitHub Builder
━━━━━━━━━━━━━━━━━━━━━━
يأخذ الـ manifest من AI Processor ويبني مستودعاً GitHub كاملاً.
"""

import os
import sys
import json
import time
import base64
import requests

# ─── الإعدادات ────────────────────────────────────────────────────
GH_PAT       = os.environ.get("GH_PAT", "")
GH_USERNAME  = os.environ.get("GH_USERNAME", "")
PROJECT_NAME = os.environ.get("PROJECT_NAME", "haa-project")
MANIFEST_PATH = "/tmp/project_manifest.json"

HEADERS = {
    "Authorization": f"Bearer {GH_PAT}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json"
}
BASE_URL = "https://api.github.com"


def load_manifest() -> dict:
    """تحميل الـ manifest من الملف."""
    if not os.path.exists(MANIFEST_PATH):
        print(f"❌ لم يُعثر على الـ manifest: {MANIFEST_PATH}")
        sys.exit(1)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def repo_exists(name: str) -> bool:
    """التحقق إذا كان المستودع موجوداً مسبقاً."""
    resp = requests.get(f"{BASE_URL}/repos/{GH_USERNAME}/{name}", headers=HEADERS)
    return resp.status_code == 200


def create_repository(name: str, description: str, private: bool = False) -> dict:
    """إنشاء مستودع GitHub جديد."""
    # إذا كان موجوداً، أضف timestamp للتمييز
    if repo_exists(name):
        ts = str(int(time.time()))[-6:]
        name = f"{name}-{ts}"
        print(f"⚠️ المستودع موجود، استخدام اسم جديد: {name}")

    payload = {
        "name": name,
        "description": description[:255] if description else f"مشروع مبني بواسطة H.A.A",
        "private": private,
        "auto_init": False,
        "has_issues": True,
        "has_projects": False,
        "has_wiki": False
    }

    resp = requests.post(f"{BASE_URL}/user/repos", headers=HEADERS, json=payload)

    if resp.status_code == 201:
        data = resp.json()
        print(f"✅ تم إنشاء المستودع: {data['html_url']}")
        return data
    else:
        print(f"❌ فشل إنشاء المستودع ({resp.status_code}): {resp.text[:300]}")
        sys.exit(1)


def upload_file(repo_name: str, file_path: str, content: str, commit_msg: str = None) -> bool:
    """رفع ملف واحد إلى المستودع."""
    # ترميز المحتوى
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    url = f"{BASE_URL}/repos/{GH_USERNAME}/{repo_name}/contents/{file_path}"
    payload = {
        "message": commit_msg or f"✨ إضافة {file_path}",
        "content": encoded,
        "branch": "main"
    }

    resp = requests.put(url, headers=HEADERS, json=payload)

    if resp.status_code in (200, 201):
        return True
    else:
        print(f"  ⚠️ فشل رفع {file_path} ({resp.status_code}): {resp.text[:200]}")
        return False


def initialize_repo_with_readme(repo_name: str, description: str) -> bool:
    """تهيئة المستودع بـ README أولي لإنشاء الـ main branch."""
    init_readme = f"# {repo_name}\n\n{description}\n\n> *جارٍ بناء المشروع بواسطة H.A.A...*\n"
    return upload_file(repo_name, "README.md", init_readme, "🚀 تهيئة المستودع")


def add_repository_topics(repo_name: str, topics: list):
    """إضافة مواضيع (Topics) للمستودع."""
    clean_topics = []
    for t in topics[:20]:  # GitHub يحدد بـ 20
        t = t.lower().replace(" ", "-").replace("_", "-")
        if t and len(t) <= 35:
            clean_topics.append(t)

    default_topics = ["haa", "auto-generated", "hussain-ali-automation"]
    all_topics = list(set(default_topics + clean_topics))[:20]

    resp = requests.put(
        f"{BASE_URL}/repos/{GH_USERNAME}/{repo_name}/topics",
        headers=HEADERS,
        json={"names": all_topics}
    )
    if resp.status_code == 200:
        print(f"🏷️ تم إضافة {len(all_topics)} مواضيع")


def create_setup_issue(repo_name: str, manifest: dict):
    """إنشاء Issue يحتوي على تعليمات الإعداد."""
    steps = manifest.get("setup_steps", [])
    env_vars = manifest.get("env_vars", [])
    features = manifest.get("features", [])

    body_parts = ["## 🚀 دليل الإعداد السريع\n"]

    if env_vars:
        body_parts.append("### 🔐 المتغيرات البيئية المطلوبة\n")
        body_parts.append("| المتغير | الوصف | مطلوب |")
        body_parts.append("|---------|-------|--------|")
        for ev in env_vars:
            req = "✅" if ev.get("required") else "⚪"
            body_parts.append(f"| `{ev['key']}` | {ev.get('description', '')} | {req} |")
        body_parts.append("")

    if steps:
        body_parts.append("### 📋 خطوات التشغيل\n")
        for i, step in enumerate(steps, 1):
            body_parts.append(f"{i}. {step}")
        body_parts.append("")

    if features:
        body_parts.append("### ✨ الميزات\n")
        for feat in features:
            body_parts.append(f"- {feat}")
        body_parts.append("")

    body_parts.append("\n---\n*تم إنشاء هذا المشروع تلقائياً بواسطة [H.A.A](https://github.com/hussain-ali/HAA)*")

    resp = requests.post(
        f"{BASE_URL}/repos/{GH_USERNAME}/{repo_name}/issues",
        headers=HEADERS,
        json={
            "title": "📚 دليل الإعداد والتشغيل",
            "body": "\n".join(body_parts),
            "labels": []
        }
    )
    if resp.status_code == 201:
        print(f"📋 تم إنشاء Issue الإعداد")


def set_github_env(key: str, value: str):
    """تعيين متغير بيئة لـ GitHub Actions."""
    env_file = os.environ.get("GITHUB_ENV", "")
    if env_file:
        with open(env_file, "a") as f:
            f.write(f"{key}={value}\n")


def main():
    if not GH_PAT:
        print("❌ GH_PAT غير موجود في Secrets")
        sys.exit(1)
    if not GH_USERNAME:
        print("❌ GH_USERNAME غير موجود")
        sys.exit(1)

    print("=" * 60)
    print("🔨 H.A.A — GitHub Builder")
    print("=" * 60)

    # تحميل الـ manifest
    manifest = load_manifest()

    # تحديد اسم المشروع
    repo_name = PROJECT_NAME or manifest.get("project_name", "haa-project")
    import re
    repo_name = re.sub(r'[^a-zA-Z0-9\-_]', '-', repo_name).lower()
    repo_name = re.sub(r'-+', '-', repo_name).strip('-')[:50]
    if not repo_name:
        repo_name = "haa-project"

    description = manifest.get("description", "مشروع مبني بواسطة H.A.A")
    files       = manifest.get("files", [])
    language    = manifest.get("language", "")
    proj_type   = manifest.get("type", "")

    print(f"📦 المستودع: {repo_name}")
    print(f"📝 الوصف: {description}")
    print(f"📁 الملفات: {len(files)}")

    # ─── 1. إنشاء المستودع ──────────────────────────────────────────
    print("\n🏗️ إنشاء المستودع...")
    repo_data = create_repository(repo_name, description)
    actual_repo_name = repo_data["name"]
    repo_url = repo_data["html_url"]

    # تأخير قصير للتأكد من إنشاء المستودع
    time.sleep(2)

    # ─── 2. تهيئة المستودع بـ README أولي ─────────────────────────
    print("\n📄 تهيئة المستودع...")
    initialize_repo_with_readme(actual_repo_name, description)
    time.sleep(1)

    # ─── 3. رفع الملفات ─────────────────────────────────────────────
    print(f"\n📤 رفع {len(files)} ملف...")
    success_count = 0
    fail_count    = 0

    for i, file_info in enumerate(files):
        path    = file_info.get("path", "")
        content = file_info.get("content", "")

        if not path or path == "README.md":
            # README يُرفع في الخطوة الأخيرة مع المحتوى الحقيقي
            continue

        print(f"  [{i+1}/{len(files)}] رفع: {path}")
        ok = upload_file(
            actual_repo_name,
            path,
            content,
            f"✨ إضافة {path} — H.A.A"
        )
        if ok:
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.3)  # تجنب rate limiting

    # رفع README الحقيقي أخيراً
    readme_file = next((f for f in files if f.get("path") == "README.md"), None)
    if readme_file:
        print(f"  📖 رفع README.md...")
        # نحتاج لحذف القديم ورفع الجديد
        # نجلب الـ SHA أولاً
        r = requests.get(
            f"{BASE_URL}/repos/{GH_USERNAME}/{actual_repo_name}/contents/README.md",
            headers=HEADERS
        )
        if r.status_code == 200:
            sha = r.json().get("sha", "")
            encoded = base64.b64encode(readme_file["content"].encode("utf-8")).decode("utf-8")
            requests.put(
                f"{BASE_URL}/repos/{GH_USERNAME}/{actual_repo_name}/contents/README.md",
                headers=HEADERS,
                json={
                    "message": "📖 تحديث README.md — H.A.A",
                    "content": encoded,
                    "sha": sha,
                    "branch": "main"
                }
            )
            success_count += 1

    # ─── 4. إضافة Topics ────────────────────────────────────────────
    topics = []
    if language:
        topics.append(language.lower())
    if proj_type:
        topics.append(proj_type.lower())
    add_repository_topics(actual_repo_name, topics)

    # ─── 5. إنشاء Issue الإعداد ─────────────────────────────────────
    if manifest.get("setup_steps") or manifest.get("env_vars"):
        create_setup_issue(actual_repo_name, manifest)

    # ─── 6. حفظ الرابط لباقي الـ Workflow ──────────────────────────
    set_github_env("CREATED_REPO_URL", repo_url)
    set_github_env("CREATED_REPO_NAME", actual_repo_name)

    # ─── ملخص ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎉 اكتمل البناء!")
    print(f"  ✅ الملفات المرفوعة: {success_count}")
    if fail_count:
        print(f"  ⚠️ الملفات الفاشلة: {fail_count}")
    print(f"  🔗 الرابط: {repo_url}")
    print("=" * 60)


if __name__ == "__main__":
    main()
