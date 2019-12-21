import os
import pandas as pd
import xlrd
from datetime import datetime


def parse_file(fname):
    try:
        wb = xlrd.open_workbook(fname)
    except FileNotFoundError:
        notFoundMsgBox = QMessageBox()
        notFoundMsgBox.setText("Файл не найден")
        notFoundMsgBox.exec()
    else:
        sheet = wb.sheet_by_index(0)
        file_name = sheet.cell_value(0, 1)
        date = sheet.cell_value(5, 1)
        date_object = datetime.strptime(date[:-4], "%m/%d/%Y %H:%M:%S")
        date = date_object.strftime("%Y-%m-%d %H:%M:%S")
        df = pd.read_excel(fname, skiprows=19)

        # перемещение использованного файла в другую директорию
        new_path = "./old_files/"
        slash_pointer = 0
        for i, symbol in enumerate(fname):
            if symbol == "/":
                slash_pointer = i
        only_file_name = fname[slash_pointer+1:]
        new_file = new_path + only_file_name
        os.rename(fname, new_file)

        df["Date"] = date
        df["File"] = file_name
        df = df.rename(index=str, columns={"Ds": "Diagnosis"})
        # ниже может быть columns=["miRNA"], проблемы с единым форматом файла
        df_new = pd.pivot_table(df, index=["Sample", "Tissue", "Diagnosis", "Date", "File"], columns=["miR"])
        df_new.columns = df_new.columns.get_level_values(1)
        df_new = df_new.reset_index(level=[0, 1, 2, 3, 4])
        normalizators = ["Blank (H2O)", "UniSp2", "UniSp3 IPC", "UniSp4", "UniSp5", "UniSp6"]
        for normalizator in normalizators:
            try:
                df_new = df_new.drop(columns=normalizator)
            except KeyError:
                pass
        return df_new
