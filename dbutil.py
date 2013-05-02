#!/usr/bin/env python2
# -*-coding:utf-8 -*-

import MySQLdb
import subprocess


class ConnectionInfos():
    def __init__(self, host="localhost", user="root", password="", port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.port = port


def tryConnect(connectionInfo):
    try:
        db = MySQLdb.connect(host=connectionInfo.host, user=connectionInfo.user, passwd=connectionInfo.password, port=connectionInfo.port)
        return db
    except MySQLdb.OperationalError:
        return None


def getDatabaseNamesAndSizes(connectionInfo):
    cur = tryConnect(connectionInfo).cursor()
    cur.execute("SELECT table_schema \"name\", sum( data_length + index_length ) / 1024 / 1024 \"size\" FROM information_schema.TABLES GROUP BY table_schema;")
    result = []
    for row in cur.fetchall():
        #skip unwanted DB
        if row[0] != 'mysql' and row[0] != 'performance_schema' and row[0] != 'information_schema':
            result.append([row[0], row[1]])
    return result


def dumpDatabase(dbName, path, connectionInfo):
    cmd = "mysqldump -u %s --password=%s -h %s --port=%s --lock-tables=false --routines --skip-comments --add-drop-database --databases %s | gzip > \"%s/%s.sql.gz\""
    cmd = cmd % (connectionInfo.user, connectionInfo.password, connectionInfo.host, connectionInfo.port, dbName, path, dbName)
    try:
        subprocess.call(cmd, shell=True)
    except OSError as e:
        print >>subprocess.sys.stderr, "Execution failed:", e

if __name__ == "__main__":
    connectionInfos = ConnectionInfos(password="")
    print getDatabaseNamesAndSizes(connectionInfos)
