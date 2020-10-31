#!/usr/bin/env bash
# SSL有効化

# 途中でエラーが発生したら即異常終了する
set -e -o pipefail

cd /var/lib/postgresql/data

# SSL証明書作成
key_filename=server.key
openssl req -x509 -nodes -new -newkey rsa:2048 -keyout ${key_filename} -out server.crt -days 365 -subj "/C=JP/ST=Tokyo/L=Tokyo/O=hato-bot Development Team/OU=hato-bot Development Team/CN=example.com"
chmod 600 ${key_filename}

# SSL設定
sed -i -e "s/#ssl = off/ssl = on/g" postgresql.conf
