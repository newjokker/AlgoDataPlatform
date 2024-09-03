


CREATE DATABASE SaturnTest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- USE Saturn_Database_V1;
USE SaturnTest;

-- DROP TABLE UcdJsonTag;

CREATE TABLE UcdJsonTag (
    tag CHAR(200) NOT NULL,
    tag_describe TEXT,
    PRIMARY KEY (tag)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

