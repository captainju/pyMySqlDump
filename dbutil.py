#!/usr/bin/env python2
# -*-coding:utf-8 -*-

import MySQLdb
import subprocess

db = MySQLdb.connect(host="localhost", user="root", passwd="", port=3306)


def getDatabasesNamesAndSizes():
    cur = db.cursor()
    cur.execute("SELECT table_schema \"name\", sum( data_length + index_length ) / 1024 / 1024 \"size\" FROM information_schema.TABLES GROUP BY table_schema;")
    result = []
    for row in cur.fetchall():
        if row[0] != 'mysql' and row[0] != 'performance_schema' and row[0] != 'information_schema':
            result.append([row[0], row[1]])
    return result


def dumpDatabase(dbName, path):
    print "dump " + dbName
    cmd = "mysqldump -u %s --password=%s --lock-tables=false --skip-comments --add-drop-database %s | gzip > \"%s/%s.sql.gz\""
    cmd = cmd % ("root", "", dbName, path, dbName)
    try:
        retcode = subprocess.call(cmd, shell=True)
        # if retcode < 0:
        #     print >>subprocess.sys.stderr, "Child was terminated by signal", -retcode
        # else:
        #     print >>subprocess.sys.stderr, "Child returned", retcode
    except OSError as e:
        print >>subprocess.sys.stderr, "Execution failed:", e

    print "finished :)"
