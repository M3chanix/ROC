import os
import pandas as pd
import xlrd
from xlutils.copy import copy
import xlwt
from datetime import datetime

# string_list = []
# f = open('unparsedMiRNA.txt')
# count = 0
# for line in f:
#     if count % 2 == 0:
#         if line[5:8] != "mir":
#             string_list.append("["+line[5:-11]+"]")
#         else:
#             string_list.append("[miR"+line[8:-11] + "]")
#     count += 1
# string_list.append("[miR-U6]")
# print(string_list)
# print(len(string_list))
# f.close()
# f = open('parsedMiRNA.txt', 'w')
# for index in string_list:
#     f.write(index + " REAL,\n")
# f.close()



# script = """
# Create table Patient_data(Sample TEXT PRIMARY KEY,
# Tissue TEXT NOT NULL,
# BIN_Diagnosis INTEGER NOT NULL,
# Source TEXT NOT NULL,
# Material TEXT NOT NULL,
# Operator_RNA_Isolation TEXT NOT NULL,
# Operator_PCR TEXT NOT NULL,
# RNA_Concentration INTEGER NOT NULL,
# Diagnosis TEXT NOT NULL,
# """

# f = open("parsedMiRNA.txt")
# for line in f:
#     script += line
# script = script[:-2]
# script += ");"
# print(script)



# mylist = []
# f = open("parsedMiRNA_no_indexes.txt")
# for line in f:
#     if line not in mylist:
#         mylist.append(line)
# f.close()
#
# f = open("parsedMiRNA_no_duplicates.txt", "w")
# for index in mylist:
#     f.write(index)
# f.close()


# loc = ("C://py1//1-goiter_mod.xls")
# wb = xlrd.open_workbook(loc)
# sheet = wb.sheet_by_index(0)
# file_name = sheet.cell_value(0, 1)
# date = sheet.cell_value(5, 1)
# date_object = datetime.strptime(date[:-4], "%m/%d/%Y %H:%M:%S")
# date = date_object.strftime("%Y-%m-%d %H:%M:%S")
# df = pd.read_excel("1-goiter_mod.xls", skiprows=14)
# print(df)
# df["Date"] = date
# df["File"] = file_name
# df = df.rename(index=str, columns={"Ds": "Diagnosis"})
# df_new = pd.pivot_table(df, index=["Sample", "Tissue", "Diagnosis", "Date", "File"], columns=["miRNA"])
# print(df_new)
# df_new.columns = df_new.columns.get_level_values(1)
# df_new = df_new.reset_index(level=[0, 1, 2, 3, 4])
# print(df_new)



# os.chdir("C://py1//machine_files")
# names = pd.DataFrame()
# for file in os.listdir("C://py1//machine_files"):
#     df = pd.read_excel(file, skiprows=19, usecols=[2])
#     names = names.append(df, ignore_index=True)
# print(len(names["Sample"].unique()))



# os.chdir("C://py1")
# string_list = []
# f = open('parsedMiRNA_no_duplicates.txt')
# for line in f:
#     string_list.append("[hsa-"+line[1:-8] + "-3p" + line[-8:])
#     string_list.append("[hsa-" + line[1:-8] + "-5p" + line[-8:])
# print(string_list)
# print(len(string_list))
# f.close()
# f = open('parsedMiRNA_5p_3p.txt', 'w')
# for index in string_list:
#     f.write(index)
# f.close()



# import sqlite3
#
# def max_columns():
#     db = sqlite3.connect(':memory:')
#     low = 1
#     high = 32767  # hard limit <http://www.sqlite.org/limits.html>
#     while low < high - 1:
#         guess = (low + high) // 2
#         try:
#             db.execute('CREATE TABLE T%d (%s)' % (
#                 guess, ','.join('C%d' % i for i in range(guess))
#             ))
#         except sqlite3.DatabaseError as ex:
#             if 'too many columns' in str(ex):
#                 high = guess
#             else:
#                 raise
#         else:
#             low = guess
#     return low
#
# print(max_columns())


# os.chdir("C://py1")
# miRNA_dict = {}
# f = open("miRNA_indexes.txt")
# for line in f:
#     key = line[:-6]
#     miRNA_dict[key] = line[:-6] + "-" + line[-3:-1]
# f.close()
# os.chdir("C://py1//group_both_files")
# miRNA_list = []
# file_count = 0
# for file in os.listdir("C://py1//group_both_files"):
#     rb = xlrd.open_workbook(file)
#     wb = copy(rb)
#     wb_sheet = wb.get_sheet(0)
#     rb_sheet = rb.sheet_by_index(0)
#     for i in range(21, rb_sheet.nrows):
#         miRNA = rb_sheet.cell_value(i, 4)
#         if miRNA[:3] == "hsa" and miRNA[-1] != "p":
#             # print(miRNA_dict[miRNA])
#             wb_sheet.write(i, 4, miRNA_dict[miRNA])
#     wb.save("C:/py1/group_both_files_parsed/" + file[:-5]+".xls")
#     file_count += 1
# print(file_count)

dick = {}
for i in range(0, 10):
    dick[i] = -i * i
print(dick)

dick1 = list(dick.items())
dick1.sort(key=lambda value: value[1])
print(dick1)


