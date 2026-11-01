-- Таблицы проекта. Сначала удаляется proposals: на неё ссылаются ключи.

DROP TABLE IF EXISTS proposals;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS managers;

CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE managers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE proposals (
    id INTEGER PRIMARY KEY,
    number TEXT NOT NULL,
    client_id INTEGER NOT NULL,
    manager_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    discount_percent REAL NOT NULL,
    created_date TEXT NOT NULL,
    validity_days INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients (id),
    FOREIGN KEY (manager_id) REFERENCES managers (id)
);
