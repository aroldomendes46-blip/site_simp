[app]
title = Vendas Comandas
package.name = vendascomandas
package.domain = br.com.vendascomandas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,kivymd
orientation = portrait
osx.package_name = VendasComandas
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.gradle_dependencies = 'androidx.appcompat:appcompat:1.6.1'
android.add_src =

[buildozer]
log_level = 2
warn_on_root = 1
