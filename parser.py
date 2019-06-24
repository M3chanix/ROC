import os
os.chdir("C://py1")
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

mylist = []
f = open("parsedMiRNA_no_indexes.txt")
for line in f:
    if line not in mylist:
        mylist.append(line)
# myset = set(mylist)
# print(len(mylist)-len(myset))
# print(len(mylist))
# print(mylist)
f.close()

f = open("parsedMiRNA_no_duplicates.txt", "w")
for index in mylist:
    f.write(index)
f.close()
