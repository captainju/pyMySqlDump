#!/usr/bin/env python
# -*-coding:utf-8 -*-

import MySQLdb


db = MySQLdb.connect(host="localhost", user="root", passwd="")


def getDatabasesNamesAndSizes():
    cur = db.cursor()
    cur.execute("SELECT table_schema \"name\", sum( data_length + index_length ) / 1024 / 1024 \"size\" FROM information_schema.TABLES GROUP BY table_schema;")
    result = []
    for row in cur.fetchall():
        if row[0] != 'mysql' and row[0] != 'performance_schema' and row[0] != 'information_schema':
            result.append([row[0], row[1]])
    return result
