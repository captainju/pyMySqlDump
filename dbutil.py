#!/usr/bin/env python2
# -*-coding:utf-8 -*-

import MySQLdb
import subprocess

host = "localhost"
user = "root"
password = ""
port = 3306

db = MySQLdb.connect(host=host, user=user, passwd=password, port=port)


def getDatabasesNamesAndSizes():
    cur = db.cursor()
    cur.execute("SELECT table_schema \"name\", sum( data_length + index_length ) / 1024 / 1024 \"size\" FROM information_schema.TABLES GROUP BY table_schema;")
    result = []
    for row in cur.fetchall():
        if row[0] != 'mysql' and row[0] != 'performance_schema' and row[0] != 'information_schema':
            result.append([row[0], row[1]])
    return result


def dumpDatabase(dbName, path):
    print "dumping " + dbName
    cmd = "mysqldump -u %s --password=%s -h %s --port=%s --lock-tables=false --routines --skip-comments --add-drop-database --databases %s | gzip > \"%s/%s.sql.gz\""
    cmd = cmd % (user, password, host, port, dbName, path, dbName)
    try:
        retcode = subprocess.call(cmd, shell=True)
        # if retcode < 0:
        #     print >>subprocess.sys.stderr, "Child was terminated by signal", -retcode
        # else:
        #     print >>subprocess.sys.stderr, "Child returned", retcode
    except OSError as e:
        print >>subprocess.sys.stderr, "Execution failed:", e

    print "finished :)"
