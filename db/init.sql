
-- psql "host=localhost port=6000 user=admin password=WeRy_HaRt_paroll dbname=wolf_butler_database"

CREATE DATABASE wolf_butler_database;

CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    chat_id SERIAL UNIQUE,
    message_list XML
);

CREATE TABLE reminders (
    reminder_id SERIAL PRIMARY KEY,
    chat_id SERIAL,
    reminder_time TIME,
    reminder_text TEXT
);

CREATE TABLE user_info (
    user_info_id SERIAL PRIMARY KEY,
    chat_id SERIAL UNIQUE,
    user_name text,
    user_callname text,
    user_utc text,
)

CREATE TABLE memory (
    item_id SERIAL PRIMARY KEY,
    chat_id SERIAL UNIQUE,
    bucket_name text,
    key_name text,
    headers_list XML,
    content text,
);