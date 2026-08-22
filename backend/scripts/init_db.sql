-- ---------------------------------------------------------------
-- ResumeIQ — one-time database bootstrap
--
-- Run with:  mysql -u root -p < backend/scripts/init_db.sql
--
-- Creates the schema and a dedicated least-privilege application user.
-- The app never connects as root: if the app is ever compromised, the
-- blast radius is limited to this one database.
-- ---------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS resume_analyzer
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'resumeiq'@'localhost'
  IDENTIFIED BY 'resumeiq_dev_pw';

GRANT ALL PRIVILEGES ON resume_analyzer.* TO 'resumeiq'@'localhost';

FLUSH PRIVILEGES;

SELECT 'resume_analyzer database and resumeiq user are ready.' AS status;
