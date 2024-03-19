--@block
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    user_type VARCHAR(255),
    password VARCHAR(255)
);

--@block
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    acc_type VARCHAR(255),
    balance FLOAT,
    interest_rate FLOAT,
    last_transaction_time TIMESTAMP,
    owner_id INT REFERENCES users(id)
);

--@block
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    acct_id INT,
    amount FLOAT,
    type VARCHAR(255),
    timestamp TIMESTAMP,
    description VARCHAR(255),
    FOREIGN KEY (acct_id) REFERENCES accounts(id)
);


-- Note: PostgreSQL does not have a direct equivalent of the MySQL ALTER TABLE tableName CHANGE command.
-- Instead, you use the ALTER TABLE RENAME COLUMN and ALTER COLUMN TYPE if necessary. Here's an example:
-- To rename a column:
--@block
ALTER TABLE tableName RENAME COLUMN oldcolname TO newcolname;

-- To change a column's data type:
--@block
ALTER TABLE tableName ALTER COLUMN colname TYPE new_datatype USING colname::new_datatype;



-- Add info for first user account
--@block
INSERT INTO  users (name, email, user_type, password)
VALUES ('Carlos', 'cjj@gmail.com', 'admin', 'test');

--@block
DELETE FROM cars
WHERE brand = 'Volvo';

--@block
UPDATE users
SET password = 'unhashed_password'
WHERE name = 'Carlos2';
