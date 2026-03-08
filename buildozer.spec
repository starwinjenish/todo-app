[app]
title = Todo App
package.name = todoapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
source.exclude_exts = spec
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,sqlite3
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

[app:android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.accept_sdk_license = True