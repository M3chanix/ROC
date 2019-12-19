#!/usr/bin/env python3
import sys
import os
import sqlite3 as sql
from model import Sample
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xlrd
from datetime import datetime
from sklearn import metrics
import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QFileDialog, QComboBox, QPushButton, \
    QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QInputDialog, QDialog, QCheckBox, QHBoxLayout, \
    QVBoxLayout, QMessageBox, QProgressDialog


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
        for symbol, i in zip(fname, range(len(fname))):
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


def save_to_sql(data):
    connection = sql.connect("Data.db")
    try:
        data.to_sql("Patient_data", connection, if_exists="append", index=False)
    except sql.IntegrityError:
        failMsgBox = QMessageBox()
        failMsgBox.setText("Этот файл уже добавлялся прежде")
        failMsgBox.exec()
    else:
        successMsgBox = QMessageBox()
        successMsgBox.setText("Данные успешно добавлены")
        successMsgBox.exec()
    connection.close()


def read_from_sql(script):
    connection = sql.connect("Data.db")
    sql_data = pd.read_sql(script, connection)
    connection.close()

    return sql_data


def get_sql_labels(sql_labels):
    sql_label_values = {}
    connection = sql.connect("Data.db")
    cursor = connection.cursor()
    query_part1 = "select distinct "
    query_part2 = " from Patient_data"
    for label in sql_labels:
        query = query_part1+label+query_part2
        cursor.execute(query)
        sql_label_values[label] = cursor.fetchall()

    cursor.close()
    connection.close()
    return sql_label_values


def alter_new_columns(patient_data):
    new_labels = set()
    for column in patient_data.columns:
        new_labels.add(column)

    con = sql.connect("Data.db")
    cur = con.cursor()
    cur.execute("PRAGMA table_info(Patient_data)")
    data = cur.fetchall()
    sql_labels = set()
    for row in data:
        sql_labels.add((row[1]))
    diff_set = new_labels.difference(sql_labels)
    for column in diff_set:
        script = "ALTER TABLE Patient_data ADD COLUMN " + "[" + column + "]" + " REAL"
        cur.execute(script)
    cur.close()
    con.close()


class SavedDataWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.table_labels = ["Sample", "Tissue", "Diagnosis", "Date", "File", "Source", "Material",
                             "Operator_RNA_Isolation",
                             "Operator_PCR", "RNA_Concentration"]
        self.sql_labels = ["Tissue", "Diagnosis", "File", "Source", "Material", "Operator_RNA_Isolation",
                           "Operator_PCR"]
        self.sql_label_values = get_sql_labels(self.sql_labels)
        self.initUI()

    def initUI(self):
        self.class_management_widget1 = ClassManagementWidget(self.table_labels, self.sql_labels, self.sql_label_values, "Класс 1")
        self.class_management_widget2 = ClassManagementWidget(self.table_labels, self.sql_labels, self.sql_label_values, "Класс 2")
        self.Hbox = QHBoxLayout()
        self.Vbox = QVBoxLayout()
        self.prepare_button = QPushButton("Провести анализ")
        self.Hbox.addWidget(self.class_management_widget1)
        self.Hbox.addWidget(self.class_management_widget2)
        self.Vbox.addLayout(self.Hbox)
        self.Vbox.addWidget(self.prepare_button)
        self.prepare_button.clicked.connect(self.prepare_analyzis)
        self.setLayout(self.Vbox)
        main_window.setGeometry(300, 200, 1500, 450)
        self.show()

    def prepare_analyzis(self):
        class1_data = self.class_management_widget1.get_checkbox_dataframe()
        class2_data = self.class_management_widget2.get_checkbox_dataframe()
        class1_data.insert(0, "Class", 1)
        class2_data.insert(0, "Class", 0)
        result_data = class1_data.append(class2_data)
        results_widget = ResultsWindow(result_data)
        main_window.setCentralWidget(results_widget)


class ClassManagementWidget(QWidget):

    def __init__(self, table_labels, sql_labels, sql_label_values, name):
        super().__init__()
        self.table_labels = table_labels
        self.sql_labels = sql_labels
        self.sql_label_values = sql_label_values
        self.name = name
        self.initUI()

    def change_all_checkboxes(self):
        tardet_state = not self.resultWidget.cellWidget(0, 0).isChecked()
        for i in range(self.resultWidget.rowCount()):
            self.resultWidget.cellWidget(i, 0).setChecked(tardet_state)

    def get_checkbox_dataframe(self):
        checked_df = pd.DataFrame(self.fullData)
        for i in range(self.resultWidget.rowCount()):
            if not self.resultWidget.cellWidget(i, 0).isChecked():
                sample = self.resultWidget.cellWidget(i, 1).text()
                file = self.resultWidget.cellWidget(i, 5).text()
                checked_df = checked_df.drop(checked_df.loc[(checked_df["Sample"] == sample) & (checked_df["File"] == file)].index)
        return checked_df

    def clearSearchResults(self):
        self.fullData = pd.DataFrame()
        self.drawSearchResults()

    def drawSearchResults(self):
        self.resultWidget.setRowCount(len(self.fullData))

        for i in range(len(self.fullData)):
            a = QCheckBox()
            a.setChecked(True)
            self.resultWidget.setCellWidget(i, 0, a)
            for j in range(len(self.table_labels)):
                a = QLabel()
                a.setText(str(self.fullData.iloc[i, j]))
                self.resultWidget.setCellWidget(i, j + 1, a)
        self.resultWidget.resizeColumnsToContents()

    def getSearcResults(self):
        script = """
        Select * From Patient_data
        """

        queryValues = []
        sql_order = [1, 2, 4, 5, 6, 7, 8]
        order = [0, 3, 9]
        for i in order:
            current_value = self.searchWidget.cellWidget(0, i).text()
            if current_value != "":
                queryValues.append('{} = "{}"'.format(self.table_labels[i], current_value))

        for i in sql_order:
            current_value = self.searchWidget.cellWidget(0, i).currentText()
            if current_value != "Any":
                queryValues.append('{} = "{}"'.format(self.table_labels[i], current_value))

        if len(queryValues) > 0:
            script += " where"
            for value in queryValues:
                script += " "
                script += value
                script += " and"
            script = script[:-3]

        self.sql_data = read_from_sql(script)
        self.sql_data = self.sql_data.dropna(axis=1, how="all")
        self.fullData = self.fullData.append(self.sql_data)
        self.fullData = self.fullData.drop_duplicates()
        self.drawSearchResults()

    def createSearchWidget(self):
        self.searchWidget.setColumnCount(len(self.table_labels))
        self.resultWidget.setColumnCount(len(self.table_labels)+1)
        self.searchWidget.setHorizontalHeaderLabels(self.table_labels)
        result_table_labels = list(self.table_labels)
        result_table_labels.insert(0, "")
        self.resultWidget.setHorizontalHeaderLabels(result_table_labels)
        self.resultWidget.resizeColumnsToContents()
        self.searchWidget.setRowCount(1)
        sql_order = [1, 2, 4, 5, 6, 7, 8]
        order = [0, 3, 9]
        for key, j in zip(self.sql_labels, sql_order):
            a = QComboBox()
            a.addItem("Any")
            for label in self.sql_label_values[key]:
                a.addItem(label[0])
            self.searchWidget.setCellWidget(0, j, a)

        for i in order:
            a = QLineEdit()
            self.searchWidget.setCellWidget(0, i, a)
        self.searchWidget.resizeColumnsToContents()

    def initUI(self):
        self.setWindowTitle("TableWidget Test")
        self.grid_layout = QGridLayout()
        self.searchWidget = QTableWidget()
        self.resultWidget = QTableWidget()
        self.fullData = pd.DataFrame()

        self.TextLabel = QLabel(self.name)
        processSearchButton = QPushButton("Добавить данные на обработку")
        # AnalyzeButton = QPushButton("Провести анализ")
        self.createSearchWidget()
        self.grid_layout.addWidget(self.TextLabel, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.searchWidget, 1, 0, 1, 2)
        self.grid_layout.addWidget(processSearchButton, 2, 0, 1, 2)
        self.grid_layout.addWidget(self.resultWidget, 3, 0, 1, 2)
        checkboxesButton = QPushButton("Выбрать/Отменить все")
        self.grid_layout.addWidget(checkboxesButton, 4, 0, 1, 1)
        clearButton = QPushButton("Очистить")
        self.grid_layout.addWidget(clearButton, 4, 1, 1, 1)
        # self.grid_layout.addWidget(AnalyzeButton)

        processSearchButton.clicked.connect(self.getSearcResults)
        checkboxesButton.clicked.connect(self.change_all_checkboxes)
        clearButton.clicked.connect(self.clearSearchResults)
        # AnalyzeButton.clicked.connect(self.prepareAnalyzis)

        self.setLayout(self.grid_layout)


class NewDataWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def createTableWidget(self):
        self.tableWidget.setColumnCount(10)
        self.table_labels = ["Sample", "Tissue", "Diagnosis", "Date", "File", "Source", "Material", "Operator_RNA_Isolation",
             "Operator_PCR", "RNA_Concentration"]
        self.sql_labels = ["Source", "Material", "Operator_RNA_Isolation", "Operator_PCR"]
        self.tableWidget.setHorizontalHeaderLabels(self.table_labels)
        self.sql_label_values = get_sql_labels(self.sql_labels)
        self.patient_table = parse_file(self.fname)
        self.tableWidget.setRowCount(len(self.patient_table))

        for i in self.patient_table.index:
            for j, column in zip(range(0, 5), self.patient_table.columns):
                self.tableWidget.setItem(i, j, QTableWidgetItem(self.patient_table.iloc[i][column]))
            for key, j in zip(self.sql_labels, range(len(self.sql_labels))):
                a = QComboBox()
                for label in self.sql_label_values[key]:
                    a.addItem(label[0])
                a.addItem("Add new...")
                a.activated.connect(self.addNewLabel)
                self.tableWidget.setCellWidget(i, j+5, a)
            self.tableWidget.setCellWidget(i, 9, QLineEdit())
            self.tableWidget.resizeColumnsToContents()

    def initUI(self):

        self.grid_layout = QGridLayout()
        self.tableWidget = QTableWidget()

        fileButton = QPushButton("Выберите файл")
        self.fnameLabel = QLabel()
        processFileButton = QPushButton("Обработать")
        self.grid_layout.addWidget(fileButton)
        self.grid_layout.addWidget(self.fnameLabel)
        saveButton = QPushButton("Сохранить в базу данных")
        self.grid_layout.addWidget(processFileButton)
        self.grid_layout.addWidget(self.tableWidget)
        self.grid_layout.addWidget(saveButton)

        fileButton.clicked.connect(self.manageFile)
        processFileButton.clicked.connect(self.createTableWidget)
        saveButton.clicked.connect(self.prepare_and_save)

        self.setLayout(self.grid_layout)

    def manageFile(self):
        fname, type = QFileDialog.getOpenFileName()
        self.fnameLabel.setText("Выбранный файл: {}".format(fname))
        self.fname = fname

    def get_sql_labels(self):
        connection = sql.connect("Data.db")
        cursor = connection.cursor()
        query_part1 = "select distinct "
        query_part2 = " from Patient_data"
        for label in self.sql_labels:
            query = query_part1+label+query_part2
            cursor.execute(query)
            self.sql_label_values[label] = cursor.fetchall()

        cursor.close()
        connection.close()

    def addNewLabel(self, e):
        if e == self.sender().count()-1:
            text, ok = QInputDialog.getText(self, 'Добавление поля', 'Введите элемент для добавления')
            if ok:
                combobox = self.sender()
                positionOfWidget = combobox.pos()
                index = self.tableWidget.indexAt(positionOfWidget)
                for i in range(self.tableWidget.rowCount()):
                    self.tableWidget.cellWidget(i, index.column()).insertItem(e, text)
                self.tableWidget.cellWidget(index.row(), index.column()).setCurrentIndex(e)

    def prepare_and_save(self):
        additional_data_dict = {}
        for j in range(self.tableWidget.columnCount()-5, self.tableWidget.columnCount()):
            column_list = []
            for i in range(self.tableWidget.rowCount()):
                if j != self.tableWidget.columnCount()-1:
                    column_list.append(self.tableWidget.cellWidget(i, j).currentText())
                else:
                    column_list.append(self.tableWidget.cellWidget(i, j).text())
            additional_data_dict[self.tableWidget.horizontalHeaderItem(j).text()] = column_list
        additional_data = pd.DataFrame(additional_data_dict)
        try:
            for i, label in zip(range(len(additional_data.columns)), additional_data.columns):
                self.patient_table.insert(len(self.patient_table.columns), label, additional_data[label])
        except ValueError:
            pass
        else:
            alter_new_columns(self.patient_table)
            save_to_sql(self.patient_table)



class FirstWindow(QWidget):
    def NewDataClicked(self):
        new_data_window = NewDataWindow()
        main_window.setCentralWidget(new_data_window)

    def SavedDataClicked(self):
        saved_data_window = SavedDataWindow()
        main_window.setCentralWidget(saved_data_window)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        SavedDataButton = QPushButton("Использовать данные из базы")
        NewDataButton = QPushButton("Внести новые данные из файла")
        label = QLabel("ROC Evaluator")
        label2 = QLabel("v1.01")
        self.hLayout.addWidget(SavedDataButton)
        self.hLayout.addWidget(NewDataButton)
        self.vLayout.addWidget(label)
        self.vLayout.addWidget(label2)
        self.vLayout.addStretch(1)
        self.vLayout.addItem(self.hLayout)
        NewDataButton.clicked.connect(self.NewDataClicked)
        SavedDataButton.clicked.connect(self.SavedDataClicked)
        self.setLayout(self.vLayout)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("MainWindow")
        self.setGeometry(300, 200, 1000, 450)
        first_window = FirstWindow()
        self.setCentralWidget(first_window)
        self.show()


class ResultsWindow(QWidget):

    def __init__(self, raw_data):
        super().__init__()
        self.initUI(raw_data)

    def initUI(self, raw_data):
        start = time.process_time()
        norm_data = self.normalization(raw_data)
        self.fpr, self.tpr, self.threshold, self.roc_auc = self.roc_analyze(norm_data)
        roc_list = self.sort_dictionary_by_value(self.roc_auc)
        print(time.process_time() - start)

        layout = QGridLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.table.setColumnCount(3)
        self.table.setRowCount(len(roc_list))
        for i, pair in zip(range(len(roc_list)), roc_list):
            c = QCheckBox()
            self.table.setItem(i, 0, QTableWidgetItem(roc_list[i][0]))
            self.table.setItem(i, 1, QTableWidgetItem(str(roc_list[i][1])))
            self.table.setCellWidget(i, 2, c)
        self.table.resizeColumnsToContents()
        draw_button = QPushButton("Построить график")
        draw_button.clicked.connect(self.draw_graph)
        layout.addWidget(draw_button)

    def draw_graph(self):
        picked_values = []
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 2).isChecked():
                picked_values.append(self.table.item(i, 0).text())

        self.draw_roc_curve(self.fpr, self.tpr, self.roc_auc, picked_values)

    def normalization(self, raw_data):
        raw_data = raw_data.dropna(axis=1, how="all")
        column_names = list(raw_data)
        norm_data = pd.DataFrame(raw_data, columns=raw_data.columns[:11])
        for divident in column_names[11:]:
            for divider in column_names[11:]:
                if divident != divider:
                    norm_data[divident + '/' + divider] = raw_data[divident] / raw_data[divider]
        norm_data = norm_data.dropna(axis=1, how="all")
        norm_data = norm_data.fillna(0)
        return norm_data

    def roc_analyze(self, norm_data):
        fpr = dict()
        tpr = dict()
        threshold = dict()
        roc_auc = dict()
        for i in norm_data.columns[11:]:
            fpr[i], tpr[i], threshold[i] = metrics.roc_curve(norm_data["Class"], norm_data[i])
            roc_auc[i] = metrics.auc(fpr[i], tpr[i])

        return fpr, tpr, threshold, roc_auc

    def sort_dictionary_by_value(self, dictionary):
        list_of_sorted_pairs = [(k, dictionary[k]) for k in sorted(dictionary.keys(), key=dictionary.get, reverse=True)]
        return list_of_sorted_pairs

    def draw_roc_curve(self, fpr, tpr, roc_auc, miRNA_names):
        fig = plt.figure()
        for i in miRNA_names:
            plt.plot(fpr[i], tpr[i], label="{0}; auc={1:0.2f}".format(i, roc_auc[i]))
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC curve')
        plt.legend(loc="lower left", bbox_to_anchor=(1.05, 0))
        plt.subplots_adjust(right=0.6)
        fig.set_size_inches(10, 5)
        plt.show()


if __name__ == '__main__':
    Session = sessionmaker(bind=create_engine('sqlite:///Data.db'))
    session = Session()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())

