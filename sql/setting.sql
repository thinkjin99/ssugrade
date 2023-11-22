CREATE DATABASE `ssugrade` USE `ssugrade`;

CREATE TABLE
    IF NOT EXISTS `users` (
        `student_number` VARCHAR(8) PRIMARY KEY,
        `fcm_token` VARCHAR(255) NOT NULL,
        `public_key` VARCHAR(128) NOT NULL,
        `grade` VARCHAR(128),
        `cookies` JSON
    );