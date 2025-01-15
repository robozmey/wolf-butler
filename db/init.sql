
CREATE DATABASE WOLF_BUTLER_DB;

CREATE TABLE sessions (
    chat_id SERIAL PRIMARY KEY,
    message_list TEXT
);

CREATE TABLE reminders (
    reminder_id SERIAL PRIMARY KEY,
    chat_id SERIAL,
    reminder_time TIME,
    reminder_text TEXT
);