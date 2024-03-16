--@block
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    user_type VARCHAR(255),
    password VARCHAR(255)
);

--@block
CREATE TABLE if NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    acc_type VARCHAR(255),
    balance FLOAT,
    interest_rate FLOAT,
    last_transaction_time DATETIME,
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

--@block
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    acct_id INT,
    amount FLOAT,
    type VARCHAR(255),
    timestamp DATETIME,
    description VARCHAR(255),
    FOREIGN KEY (acct_id) REFERENCES accounts(id)
);

--@block
ALTER TABLE tableName CHANGE oldcolname newcolname datatype(length);
