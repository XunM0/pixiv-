import sqlite3
import pandas as pd
import pandas.io.sql
import configparser
import os
config = configparser.RawConfigParser()
config.read("/home/ly/Item/flask/config/config.ini")

databaseUrl = config.get("database","database")
print(databaseUrl)
#databaseUrl = "/home/ly/Item/flask/dataSql.DB"
#print(databaseUrl)
conn = sqlite3.connect(databaseUrl)
cur = conn.cursor()
def insert(data):
    global conn
    data.to_sql('test',conn,index=False,if_exists='append')

def select_data(sql):
    global conn
    data = pd.read_sql(sql,conn)
    #data = data.drop(columns='index')
    return data
