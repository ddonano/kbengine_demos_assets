# -*- coding: utf-8 -*-

def getConcatSql(sql, *lists):
    tmp = sql
    for i in lists:
        tmp = tmp.replace("%s", i, 1)
    return tmp
