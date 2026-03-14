-- ============================================
-- Escape Room ERP Database - Schema Creation
-- CSE 4/560 DMQL Project
-- ============================================
-- Run this FIRST before loading insert_data.sql
-- Target: PostgreSQL
-- ============================================

-- Drop tables in reverse dependency order (if re-creating)
DROP TABLE IF EXISTS session_clues CASCADE;
DROP TABLE IF EXISTS session_employees CASCADE;
DROP TABLE IF EXISTS employee_leaves CASCADE;
DROP TABLE IF EXISTS salaries CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS game_sessions CASCADE;
DROP TABLE IF EXISTS clues CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS customers CASCADE;


-- ============================================
-- 1. Customers
-- ============================================
CREATE TABLE customers (
    customer_id    SERIAL       PRIMARY KEY,
    first_name     TEXT         NOT NULL,
    last_name      TEXT         NOT NULL,
    email          TEXT         NOT NULL UNIQUE,
    phone          TEXT,
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);


-- ============================================
-- 2. Employees
-- ============================================
CREATE TABLE employees (
    employee_id    SERIAL         PRIMARY KEY,
    name           TEXT           NOT NULL,
    role           TEXT           NOT NULL
                                 CHECK (role IN ('GameMaster', 'Manager', 'Admin')),
    hourly_rate    NUMERIC(8,2)   NOT NULL
                                 CHECK (hourly_rate > 0),
    hire_date      DATE           NOT NULL
                                 CHECK (hire_date <= CURRENT_DATE)
);


-- ============================================
-- 3. Games
-- ============================================
CREATE TABLE games (
    game_id           SERIAL    PRIMARY KEY,
    game_name         TEXT      NOT NULL,
    difficulty_level  INT       NOT NULL
                               CHECK (difficulty_level BETWEEN 1 AND 5),
    duration_minutes  INT       NOT NULL
                               CHECK (duration_minutes > 0),
    max_players       INT       NOT NULL
                               CHECK (max_players > 0)
);


-- ============================================
-- 4. Rooms
-- ============================================
CREATE TABLE rooms (
    room_id      SERIAL    PRIMARY KEY,
    room_name    TEXT       NOT NULL UNIQUE,
    capacity     INT        NOT NULL
                            CHECK (capacity > 0),
    game_id      INT        NOT NULL
                            REFERENCES games(game_id)
                            ON DELETE RESTRICT
);


-- ============================================
-- 5. Bookings
-- ============================================
-- NOTE: The CHECK (booking_date >= CURRENT_DATE) constraint is omitted here
-- because we load historical data. For production, uncomment the constraint
-- or add it after loading seed data:
--   ALTER TABLE bookings ADD CONSTRAINT bookings_booking_date_check
--   CHECK (booking_date >= CURRENT_DATE);

CREATE TABLE bookings (
    booking_id    SERIAL    PRIMARY KEY,
    customer_id   INT       NOT NULL
                            REFERENCES customers(customer_id)
                            ON DELETE CASCADE,
    booking_date  DATE      NOT NULL,
    num_players   INT       NOT NULL
                            CHECK (num_players > 0),
    status        TEXT      NOT NULL
                            CHECK (status IN ('CONFIRMED', 'CANCELLED', 'COMPLETED')),
    game_id       INT       NOT NULL
                            REFERENCES games(game_id)
                            ON DELETE RESTRICT
);


-- ============================================
-- 6. Game Sessions
-- ============================================
CREATE TABLE game_sessions (
    session_id    SERIAL       PRIMARY KEY,
    booking_id    INT          NOT NULL UNIQUE
                               REFERENCES bookings(booking_id)
                               ON DELETE CASCADE,
    game_id       INT          NOT NULL
                               REFERENCES games(game_id)
                               ON DELETE RESTRICT,
    room_id       INT          NOT NULL
                               REFERENCES rooms(room_id)
                               ON DELETE RESTRICT,
    start_time    TIMESTAMP    NOT NULL,
    end_time      TIMESTAMP    NOT NULL
                               CHECK (end_time > start_time),
    success       BOOLEAN      DEFAULT NULL
);


-- ============================================
-- 7. Session Employees (Junction Table)
-- ============================================
CREATE TABLE session_employees (
    session_id     INT    NOT NULL
                          REFERENCES game_sessions(session_id)
                          ON DELETE CASCADE,
    employee_id    INT    NOT NULL
                          REFERENCES employees(employee_id)
                          ON DELETE CASCADE,
    PRIMARY KEY (session_id, employee_id)
);


-- ============================================
-- 8. Clues
-- ============================================
CREATE TABLE clues (
    clue_id        SERIAL    PRIMARY KEY,
    game_id        INT       NOT NULL
                             REFERENCES games(game_id)
                             ON DELETE CASCADE,
    clue_text      TEXT      NOT NULL,
    time_penalty   INT       NOT NULL
                             CHECK (time_penalty >= 0)
);


-- ============================================
-- 9. Session Clues (Junction Table)
-- ============================================
CREATE TABLE session_clues (
    session_id    INT          NOT NULL
                               REFERENCES game_sessions(session_id)
                               ON DELETE CASCADE,
    clue_id       INT          NOT NULL
                               REFERENCES clues(clue_id)
                               ON DELETE CASCADE,
    used_at       TIMESTAMP    DEFAULT NULL,
    PRIMARY KEY (session_id, clue_id)
);


-- ============================================
-- 10. Payments
-- ============================================
CREATE TABLE payments (
    payment_id       SERIAL          PRIMARY KEY,
    booking_id       INT             NOT NULL
                                     REFERENCES bookings(booking_id)
                                     ON DELETE CASCADE,
    amount           NUMERIC(10,2)   NOT NULL
                                     CHECK (amount > 0),
    payment_method   TEXT            NOT NULL
                                     CHECK (payment_method IN ('Card', 'Cash', 'Online')),
    payment_status   TEXT            NOT NULL
                                     CHECK (payment_status IN ('SUCCESS', 'FAILED', 'PENDING')),
    payment_time     TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- ============================================
-- 11. Salaries
-- ============================================
CREATE TABLE salaries (
    salary_id      SERIAL          PRIMARY KEY,
    employee_id    INT             NOT NULL
                                   REFERENCES employees(employee_id)
                                   ON DELETE CASCADE,
    month          DATE            NOT NULL,
    total_hours    INT             NOT NULL
                                   CHECK (total_hours >= 0),
    total_pay      NUMERIC(10,2)   NOT NULL
                                   CHECK (total_pay >= 0),
    UNIQUE (employee_id, month)
);


-- ============================================
-- 12. Employee Leaves
-- ============================================
CREATE TABLE employee_leaves (
    leave_id       SERIAL    PRIMARY KEY,
    employee_id    INT       NOT NULL
                             REFERENCES employees(employee_id)
                             ON DELETE CASCADE,
    start_date     DATE      NOT NULL,
    end_date       DATE      NOT NULL
                             CHECK (end_date >= start_date),
    reason         TEXT
);


-- ============================================
-- Verification: Check all tables were created
-- ============================================
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
