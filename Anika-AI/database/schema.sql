-- Anika AI Database Schema
-- Designed for SQLite (can be easily migrated to MySQL)

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(150) NOT NULL,
    budget FLOAT DEFAULT 1000.0
);

CREATE TABLE IF NOT EXISTS expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount FLOAT NOT NULL,
    category VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    price FLOAT NOT NULL,
    recommendation VARCHAR(50),
    score FLOAT,
    user_id INTEGER NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
