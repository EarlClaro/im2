-- schema.sql

-- Create database
CREATE DATABASE IF NOT EXISTS notes;

-- Use the notes database
USE notes;

-- Create the 'emails' table
CREATE TABLE IF NOT EXISTS emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create the 'users' table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Create the 'userprofile' table connected with 'users'
CREATE TABLE IF NOT EXISTS userprofile (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    first_name VARCHAR(255),
    middle_name VARCHAR(255),
    last_name VARCHAR(255),
    bio TEXT,
    birthdate DATE,
    gender VARCHAR(10), -- Assuming 'gender' is a string like 'Male', 'Female', etc.
    location VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- Create the 'notes' table
CREATE TABLE IF NOT EXISTS notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    content TEXT,
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create a view named 'email_view'
CREATE OR REPLACE VIEW email_view AS
SELECT id, email, name
FROM emails;

-- Create a stored procedure to insert an email
DELIMITER //
CREATE PROCEDURE insert_email(IN p_email VARCHAR(255), IN p_name VARCHAR(255))
BEGIN
    INSERT INTO emails (email, name) VALUES (p_email, p_name);
END //
DELIMITER ;

-- Create a trigger to automatically update the 'name' column in 'emails' when a user is updated
DELIMITER //
CREATE TRIGGER update_email_name
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE emails
    SET name = NEW.username
    WHERE email = OLD.email;
END //
DELIMITER ;
