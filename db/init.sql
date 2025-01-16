
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