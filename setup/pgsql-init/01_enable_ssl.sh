#!/usr/bin/env bash
# SSL有効化

# 途中でエラーが発生したら即異常終了する
set -e -o pipefail

cd /var/lib/postgresql/data

# SSL証明書作成
key_filename=server.key
csr_filename=server.csr
crt_filename=server.crt
openssl genrsa 2048 > ${key_filename}
chmod 600 ${key_filename}
openssl req -new -key ${key_filename} -subj "/C=GB/ST=London/L=London/O=Global Security/OU=IT Department/CN=example.com" > ${csr_filename}
openssl x509 -days 36500 -req -signkey ${key_filename} < ${csr_filename} > ${crt_filename}
chown postgres:postgres ${key_filename} ${csr_filename} ${crt_filename}

# SSL設定
echo "hostssl all             all             0.0.0.0/0               md5" >> pg_hba.conf
sed -i -e "s/#ssl = off/ssl = on/g" postgresql.conf
