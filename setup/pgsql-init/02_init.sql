CREATE TABLE IF NOT EXISTS vocabulary
(
    no SERIAL UNIQUE,
    word TEXT
);
CREATE TABLE IF NOT EXISTS slack_client_msg_id
(
    client_msg_id TEXT UNIQUE,
    created_at TIMESTAMP
);
