# 🐘 PostgreSQL CLI Commands Cheat Sheet

## 🧩 Connection & Basics
| Action | Command |
|--------|----------|
| Connect to PostgreSQL | `psql -U username -d dbname` |
| Connect with host/port | `psql -h host -p port -U username -d dbname` |
| List all databases | `\l` or `\list` |
| Connect to a database | `\c dbname` or `\connect dbname` |
| Show current connection info | `\conninfo` |
| Quit psql | `\q` |

---

## 🏗️ Database Operations
| Action | Command |
|--------|----------|
| Create database | `CREATE DATABASE dbname;` |
| Delete database | `DROP DATABASE dbname;` |
| Rename database | `ALTER DATABASE oldname RENAME TO newname;` |
| Show all databases | `\l` |

---

## 🧱 Table Operations
| Action | Command |
|--------|----------|
| Show all tables | `\dt` |
| Show tables in specific schema | `\dt schema_name.*` |
| Describe table structure | `\d tablename` |
| Create table | `CREATE TABLE tablename (...);` |
| Drop table | `DROP TABLE tablename;` |
| Truncate table (delete all rows) | `TRUNCATE TABLE tablename;` |
| Rename table | `ALTER TABLE oldname RENAME TO newname;` |
| Show indexes | `\di` |

---

## 📜 Schema Operations
| Action | Command |
|--------|----------|
| List all schemas | `\dn` |
| Create schema | `CREATE SCHEMA schemaname;` |
| Drop schema | `DROP SCHEMA schemaname CASCADE;` |

---

## 👤 User & Role Management
| Action | Command |
|--------|----------|
| List all roles/users | `\du` |
| Create user | `CREATE USER username WITH PASSWORD 'password';` |
| Create role | `CREATE ROLE rolename;` |
| Grant privileges | `GRANT ALL PRIVILEGES ON DATABASE dbname TO username;` |
| Revoke privileges | `REVOKE ALL PRIVILEGES ON DATABASE dbname FROM username;` |
| Change password | `ALTER USER username WITH PASSWORD 'newpassword';` |
| Drop user | `DROP USER username;` |

---

## 📦 Data Operations
| Action | Command |
|--------|----------|
| Show all rows | `SELECT * FROM tablename;` |
| Insert data | `INSERT INTO tablename (col1, col2) VALUES ('a', 'b');` |
| Update data | `UPDATE tablename SET column='value' WHERE id=1;` |
| Delete data | `DELETE FROM tablename WHERE id=1;` |
| Import CSV | `\copy tablename FROM 'path/to/file.csv' DELIMITER ',' CSV HEADER;` |
| Export CSV | `\copy tablename TO 'path/to/file.csv' DELIMITER ',' CSV HEADER;` |

---

## ⚙️ Maintenance & Utilities
| Action | Command |
|--------|----------|
| Show PostgreSQL version | `SELECT version();` |
| Show current database | `SELECT current_database();` |
| Show current user | `SELECT current_user;` |
| List extensions | `\dx` |
| Install extension | `CREATE EXTENSION extension_name;` |
| Drop extension | `DROP EXTENSION extension_name;` |
| View running queries | `SELECT * FROM pg_stat_activity;` |

---

## 🧮 Backup & Restore
| Action | Command |
|--------|----------|
| Backup database | `pg_dump dbname > backup.sql` |
| Backup with schema only | `pg_dump -s dbname > schema.sql` |
| Backup with data only | `pg_dump -a dbname > data.sql` |
| Restore database | `psql -U username -d dbname -f backup.sql` |
| Restore with pg_restore (for .dump files) | `pg_restore -U username -d dbname backup.dump` |

---

## 🔍 Search & Filtering
| Action | Command |
|--------|----------|
| Search for table name | `\dt *pattern*` |
| Search function | `\df *pattern*` |
| Search view | `\dv *pattern*` |
| Show all sequences | `\ds` |
