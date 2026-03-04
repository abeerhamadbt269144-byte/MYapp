[app]
# (اسم التطبيق الظاهر للمستخدم)
title = Shadow Steganography

# (اسم الحزمة البرمجية)
package.name = shadowstego
package.domain = org.shadow

# (مكان الملفات)
source.dir = .
source.include_exts = py,png,jpg,kv,ttf

# (نسخة التطبيق)
version = 3.0

# --- الأهم: المكتبات المطلوبة لعمل كود التشفير ومعالجة الصور ---
# يجب إضافة cryptography و numpy و pillow و openssl
requirements = python3,kivy==2.3.0,pillow,numpy,cryptography,openssl,hostpython3

# (أيقونة التطبيق - تأكد أن الملف اسمه icon.png بجانب main.py)
icon.filename = %(source.dir)s/icon.png

# (وضع العرض - يفضل portrait للتطبيقات التي تحتوي نصوص كثيرة)
orientation = portrait

# --- صلاحيات الأندرويد للوصول للذاكرة وحفظ الصور المستخرجة ---
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21

# (بما أنك تستخدم numpy ومكتبات C، يفضل تحديد الـ architecture)
android.archs = arm64-v8a, armeabi-v7a

# (إضافة ميزة قبول التراخيص تلقائياً)
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1