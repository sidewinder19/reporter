#!/bin/sh
mysql --host $db --port 3306 --user root -p$MYSQL_ROOT_PASSWORD employees < test_db/employees.sql
