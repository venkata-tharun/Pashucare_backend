-- PashuCare Database Schema
-- Run: mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS pashucare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pashucare;

-- ─── Users ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(255) NOT NULL,
    email_or_phone VARCHAR(255) NOT NULL UNIQUE,
    farm_name   VARCHAR(255) NOT NULL DEFAULT '',
    password_hash VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── Animals ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS animals (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id  INT NOT NULL,
    name     VARCHAR(255) NOT NULL,
    tag      VARCHAR(100) NOT NULL,
    breed    VARCHAR(100) NOT NULL DEFAULT '',
    status   ENUM('Healthy','Sick') NOT NULL DEFAULT 'Healthy',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Health Records ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS health_records (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    animal_id  INT NOT NULL,
    date       DATE NOT NULL,
    title      VARCHAR(255) NOT NULL,
    status     VARCHAR(100) NOT NULL DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
);

-- ─── Vaccination Records ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vaccinations (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    animal_id     INT NOT NULL,
    vaccine_name  VARCHAR(255) NOT NULL,
    date_given    DATE NOT NULL,
    next_due_date DATE NOT NULL,
    batch_number  VARCHAR(100) DEFAULT '',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
);

-- ─── Milk Entries ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS milk_entries (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL,
    milk_type        ENUM('Bulk Milk','Individual Milk') NOT NULL DEFAULT 'Bulk Milk',
    date             DATE NOT NULL,
    cattle_tag       VARCHAR(100) DEFAULT '',
    am               DECIMAL(8,2) NOT NULL DEFAULT 0,
    noon             DECIMAL(8,2) NOT NULL DEFAULT 0,
    pm               DECIMAL(8,2) NOT NULL DEFAULT 0,
    total_used       DECIMAL(8,2) NOT NULL DEFAULT 0,
    cow_milked_number INT NOT NULL DEFAULT 0,
    note             TEXT DEFAULT '',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Transactions ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    category   ENUM('Income','Expense') NOT NULL,
    date       DATE NOT NULL,
    type       VARCHAR(100) NOT NULL,
    amount     DECIMAL(12,2) NOT NULL,
    receipt_no VARCHAR(100) DEFAULT '',
    note       TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);



-- ─── Visitors ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS visitors (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    name            VARCHAR(255) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    purpose         VARCHAR(255) DEFAULT '',
    date            DATE NOT NULL,
    entry_time      DATETIME NOT NULL,
    outgoing_time   DATETIME NOT NULL,
    person_to_meet  VARCHAR(255) DEFAULT '',
    vehicle_number  VARCHAR(50) DEFAULT '',
    notes           TEXT DEFAULT '',
    status          ENUM('Pending','Approved','Rejected','Checked In','Checked Out') NOT NULL DEFAULT 'Pending',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Calving Records ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS calving_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    animal_name     VARCHAR(255) NOT NULL,
    breeding_date   DATE NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Feed Stock ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feed_stock (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    name       VARCHAR(255) NOT NULL,
    quantity   DECIMAL(10,2) NOT NULL DEFAULT 0,
    status     ENUM('Good','Medium','Low') NOT NULL DEFAULT 'Good',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Feed Activity ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feed_activity (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    item_name    VARCHAR(255) NOT NULL,
    amount_added DECIMAL(10,2) NOT NULL,
    date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- ─── Farm Logs ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS farm_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    type        VARCHAR(100) NOT NULL,
    date        DATE NOT NULL,
    description TEXT NOT NULL,
    animal_id   VARCHAR(100),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Sanitation Scores ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sanitation_scores (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    score       INT NOT NULL,
    tasks_json  TEXT,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── AI Predictions ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai_predictions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    disease_name    VARCHAR(255) NOT NULL,
    confidence      VARCHAR(50) NOT NULL,
    status          VARCHAR(50) NOT NULL,
    symptoms_json   TEXT,
    precautions_json TEXT,
    image_path      VARCHAR(512),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
