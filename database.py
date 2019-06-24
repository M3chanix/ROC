import pandas as pd
import os
import sqlite3 as sql
os.chdir("C:/py1")

con = sql.connect("db1.db")
cur = con.cursor()
cur.execute('Select * from Patient_data')
data = cur.fetchall()
for row in data:
    print(row)
print(len(data))

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


# script = """
# Create table Patient_data(Sample TEXT PRIMARY KEY ON CONFLICT IGNORE,
# Tissue TEXT NOT NULL,
# BIN_Diagnosis TEXT NOT NULL,
# Source TEXT NOT NULL,
# Material TEXT NOT NULL,
# Operator_RNA_Isolation TEXT NOT NULL,
# Operator_PCR TEXT NOT NULL,
# RNA_Concentration REAL NOT NULL,
# Diagnosis TEXT NOT NULL,
# """
#
# f = open("parsedMiRNA_no_duplicates.txt")
# for line in f:
#     script += line
# script = script[:-2]
# script += ");"
# print(script)
#
# cur.execute(script)


cur.close()
con.close()
