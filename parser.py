import os
import pandas as pd
import xlrd
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



os.chdir("C://py1//machine_files")
names = pd.DataFrame()
for file in os.listdir("C://py1//machine_files"):
    df = pd.read_excel(file, skiprows=19, usecols=[2])
    names = names.append(df, ignore_index=True)
print(len(names["Sample"].unique()))
