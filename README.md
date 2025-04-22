# EECS 447 Project

## Running MariaDB

1. Log into cycle servers
2. Run `mysql -h mysql.eecs.ku.edu -u USER_ID -p`
    - Replace USER_ID with your user id 
    - You will then be prompted to enter your password
3. Use `\q` to quit.

## Initializing and Populating the Database

1. Select the database (447s25_j776w781)
    - `USE [db_name];`
2. Run our library script to initialize tables:
    - `SOURCE [file_path];`
    - If you ran `mysql` from the root of the github directoy, `[file_path]` can be a relative path, i.e. `./librarydb.sql`
3. In a new terminal, run `data_insert.py`
    - `cd scripts/`
    - Then, follow the `README.md` to setup the enviroment
    - Finally, run `python3 data_insert.py`
4. Verify by checking tables

## Useful commands

Show all databases:
* `SHOW DATABASES;`

Use a database:
* `USE [db_name];`

Show all tables:
* `SHOW TABLES;`

Run our library script to init tables:
* `SOURCE [file_path];`

Show columns in a table:
* `SHOW COLUMNS FROM [table_name];`

Show entries in a table:
* `SELECT * FROM [table_name];`
