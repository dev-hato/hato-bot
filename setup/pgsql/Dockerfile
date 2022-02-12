FROM postgres:14.2-alpine

# 実行時に必要なパッケージ (グループ名: .used-packages)
# * openssl: PostgreSQLとSSL通信する時に必要。
RUN apk add --no-cache -t .used-packages openssl
