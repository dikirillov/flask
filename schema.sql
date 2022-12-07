drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    username text not null,
    email text not null,
    password_hash text not null,
    full_name text not null,
    birth_date text not null,
    contact_email text not null,
    contact_phone text not null
);