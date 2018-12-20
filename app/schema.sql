DROP TABLE IF EXISTS document;

CREATE TABLE document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    plaintiff TEXT NOT NULL,
    defendants TEXT NOT NULL
);