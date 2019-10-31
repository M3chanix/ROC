import pandas as pd
import os
import sqlite3 as sql
os.chdir("C:/ROC")

con = sql.connect("Data.db")
cur = con.cursor()
# cur.execute("SELECT sql FROM sqlite_master")
# cur.execute("PRAGMA table_info(Patient_data)")
# cur.execute("Insert into Patient_data(column_name) values(1)")
# cur.execute("Select sql from sqlite_master where name = 'Patient_data';")
# cur.execute("Drop table Patient_data")
cur.execute('Select * from Patient_data')
data = cur.fetchall()
for row in data:
    print(row)
#     print(len(row))
# print(set)
# print(len(set))
# print(len(data))

# script = """
# Create table Patient_data(Sample TEXT PRIMARY KEY,
# [T-issue] TEXT NOT NULL);
# """

# labels = ["Sample", "Tissue", "Material"]
# part1 = "select distinct "
# part2 = " from Patient_data"
# for label in labels:
#     script = part1+label+part2
#     cur.execute(script)
#     print(cur.fetchall())


script = """
Create table Patient_data(Sample TEXT NOT NULL,
Tissue TEXT NOT NULL,
Diagnosis TEXT NOT NULL,
Date TEXT NOT NULL,
File TEXT NOT NULL,
Source TEXT NOT NULL,
Material TEXT NOT NULL,
Operator_RNA_Isolation TEXT NOT NULL,
Operator_PCR TEXT NOT NULL,
RNA_Concentration REAL NOT NULL,
UNIQUE(Sample, File));
"""
#
# f = open("C:/py1/parsedMiRNA_no_duplicates.txt")
# for line in f:
#     script += line
# script = script[:-2]
# script += ");"
# print(script)

# cur.execute(script)


cur.close()
con.close()
