CREATE TABLE car_price_app_studentregistration (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    full_name varchar(120) NOT NULL,
    roll_number varchar(50) NOT NULL,
    email varchar(254) NOT NULL,
    department varchar(120) NOT NULL,
    college varchar(160) NOT NULL,
    created_at datetime NOT NULL
);

CREATE TABLE car_price_app_executionlog (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    algorithm varchar(120) NOT NULL,
    dataset varchar(120) NOT NULL,
    rows_executed integer unsigned NOT NULL CHECK (rows_executed >= 0),
    created_at datetime NOT NULL
);

