#!/usr/bin/env python3

from typing import Dict

import sys
import os
import time
from datetime import datetime

import sqlite3
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import xlrd

import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QFileDialog, QComboBox, QPushButton, \
    QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QInputDialog, QDialog, QCheckBox, QHBoxLayout, \
    QVBoxLayout, QMessageBox, QProgressDialog

import numpy
import pandas
from sklearn import metrics
from itertools import permutations

from model import Sample
from parser import parse_file

engine = create_engine('sqlite:///Data.db')
MySession = sessionmaker(bind=engine)
session: Session  = MySession()


def save_to_sql(data):
    connection = sqlite3.connect("Data.db")
    try:
        data.to_sql("Patient_data", connection, if_exists="append", index=False)
    except sqlite3.IntegrityError:
        failMsgBox = QMessageBox()
        failMsgBox.setText("Этот файл уже добавлялся прежде")
        failMsgBox.exec()
    else:
        successMsgBox = QMessageBox()
        successMsgBox.setText("Данные успешно добавлены")
        successMsgBox.exec()
    connection.close()


def get_sql_labels(sql_labels):
    sql_label_values = {}
    for label in sql_labels:
        query = session.query(label).distinct()
        sql_label_values[label] = [i[0] for i in query]

    return sql_label_values


def alter_new_columns(patient_data):
    new_labels = set()
    for column in patient_data.columns:
        new_labels.add(column)

    con = sqlite3.connect("Data.db")
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
        self.sql_labels = [
            Sample.Tissue,
            Sample.Diagnosis,
            Sample.File,
            Sample.Source,
            Sample.Material,
            Sample.Operator_RNA_Isolation,
            Sample.Operator_PCR,
        ]
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
        result_data: pandas.DataFrame = class1_data.append(class2_data)
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

    def get_checkbox_dataframe(self) -> pandas.DataFrame:
        checked_df = pandas.DataFrame(self.fullData)
        for i in range(self.resultWidget.rowCount()):
            if not self.resultWidget.cellWidget(i, 0).isChecked():
                sample = self.resultWidget.cellWidget(i, 1).text()
                file = self.resultWidget.cellWidget(i, 5).text()
                checked_df = checked_df.drop(checked_df.loc[(checked_df["Sample"] == sample) & (checked_df["File"] == file)].index)
        return checked_df

    def clearSearchResults(self):
        self.fullData = pandas.DataFrame()
        self.drawSearchResults()

    def drawSearchResults(self):
        self.resultWidget.setRowCount(len(self.fullData))

        for i in range(len(self.fullData)):
            a = QCheckBox()
            a.setChecked(True)
            self.resultWidget.setCellWidget(i, 0, a)
            for j, column_name in enumerate(self.table_labels):
                a = QLabel()
                a.setText(str(self.fullData[column_name][i]))
                self.resultWidget.setCellWidget(i, j + 1, a)
        self.resultWidget.resizeColumnsToContents()

    def getSearcResults(self):
        query = session.query(Sample)

        sql_order = [1, 2, 4, 5, 6, 7, 8]
        order = [0, 3, 9]
        columns = [
            Sample.Sample,
            Sample.Tissue,
            Sample.Diagnosis,
            Sample.Date,
            Sample.File,
            Sample.Source,
            Sample.Material,
            Sample.Operator_RNA_Isolation,
            Sample.Operator_PCR,
            Sample.RNA_Concentration,
        ]
        for i in order:
            current_value = self.searchWidget.cellWidget(0, i).text()
            if current_value:
                query = query.filter(columns[i] == current_value)

        for i in sql_order:
            current_value = self.searchWidget.cellWidget(0, i).currentText()
            if current_value != "Any":
                query = query.filter(columns[i] == current_value)

        self.sql_data: pandas.DataFrame = pandas.read_sql(query.statement, session.bind).dropna(axis=1, how="all")
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
                a.addItem(label)
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
        self.fullData = pandas.DataFrame()

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
        self.sql_labels = [
            Sample.Source,
            Sample.Material,
            Sample.Operator_RNA_Isolation,
            Sample.Operator_PCR,
        ]
        self.tableWidget.setHorizontalHeaderLabels(self.table_labels)
        self.sql_label_values = get_sql_labels(self.sql_labels)
        self.patient_table = parse_file(self.fname)
        self.tableWidget.setRowCount(len(self.patient_table))

        for i in self.patient_table.index:
            for j, column in zip(range(0, 5), self.patient_table.columns):
                self.tableWidget.setItem(i, j, QTableWidgetItem(self.patient_table.iloc[i][column]))
            for j, key in enumerate(self.sql_labels):
                a = QComboBox()
                for label in self.sql_label_values[key]:
                    a.addItem(label)
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
        additional_data = pandas.DataFrame(additional_data_dict)
        try:
            for label in additional_data.columns:
                self.patient_table.insert(len(self.patient_table.columns), label, additional_data[label])
        except ValueError:
            pass
        else:
            alter_new_columns(self.patient_table)
            save_to_sql(self.patient_table)



class FirstWindow(QWidget):

    @staticmethod
    def NewDataClicked():
        new_data_window = NewDataWindow()
        main_window.setCentralWidget(new_data_window)

    @staticmethod
    def SavedDataClicked():
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


class ROC_curve_data:

    def __init__(self, fpr: numpy.ndarray, tpr: numpy.ndarray, threshold: numpy.ndarray, auc: float):
        self.fpr : numpy.ndarray = fpr
        self.tpr : numpy.ndarray = tpr
        self.threshold : numpy.ndarray = threshold
        self.auc : float = auc


class ResultsWindow(QWidget):

    def __init__(self, raw_data: pandas.DataFrame):
        super().__init__()
        self.initUI(raw_data)

    def initUI(self, raw_data: pandas.DataFrame):
        start = time.process_time()
        norm_data = self.normalization(raw_data)
        self.roc_data = self.roc_analyze(norm_data)
        print(time.process_time() - start)

        layout = QGridLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.table.setColumnCount(3)
        self.table.setRowCount(len(self.roc_data))
        value: ROC_curve_data
        for i, (key, value) in enumerate(sorted(self.roc_data.items(), key=lambda pair: pair[1].auc, reverse=True)):
            c = QCheckBox()
            self.table.setItem(i, 0, QTableWidgetItem(key))
            self.table.setItem(i, 1, QTableWidgetItem(str(value.auc)))
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

        self.draw_roc_curve(self.roc_data, picked_values)

    @staticmethod
    def normalization(raw_data: pandas.DataFrame) -> pandas.DataFrame:
        # TODO remove 11 from here
        raw_data = raw_data.dropna(axis=1, how="all")
        column_names = list(raw_data)
        norm_data = pandas.DataFrame(raw_data, columns=raw_data.columns[:11])
        result = all_divs(numpy.array(raw_data.iloc[:,11:]))
        result_df = pandas.DataFrame(result, columns=map(lambda pair: '{}/{}'.format(*pair), permutations(column_names[11:], 2)), index=norm_data.index)
        norm_data = pandas.concat([norm_data, result_df], axis='columns')
        norm_data = norm_data.dropna(axis=1, how="all")
        norm_data = norm_data.fillna(0)
        return norm_data

    @staticmethod
    def roc_analyze(norm_data: pandas.DataFrame) -> Dict[str, ROC_curve_data]:
        result = {}
        for i in norm_data.columns[11:]:
            fpr, tpr, threshold = metrics.roc_curve(norm_data["Class"], norm_data[i])
            roc_auc = metrics.auc(fpr, tpr)
            result[i] = ROC_curve_data(fpr=fpr, tpr=tpr, threshold=threshold, auc=roc_auc)
        return result

    @staticmethod
    def draw_roc_curve(roc_data: Dict[str, ROC_curve_data], miRNA_names):
        fig = plt.figure()
        for name in miRNA_names:
            plt.plot(roc_data[name].fpr, roc_data[name].tpr, label="{0}; auc={1:0.2f}".format(name, roc_data[name].auc))
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


def all_divs(data: numpy.ndarray) -> numpy.ndarray:
    '''
    >>> from numpy import array
    >>> arg = array([[1, 2, 8],   \
                     [3, 4, 6],   \
                     [5, 6, 8]])
    >>> all_divs(arg) == array([[1/2, 1/8, 2/1, 2/8, 8/1, 8/2],  \
                                [3/4, 3/6, 4/3, 4/6, 6/3, 6/4],  \
                                [5/6, 5/8, 6/5, 6/8, 8/5, 8/6]])
    array([[ True,  True,  True,  True,  True,  True],
           [ True,  True,  True,  True,  True,  True],
           [ True,  True,  True,  True,  True,  True]])
    '''
    row_count, col_count = data.shape
    permutations_count = col_count * (col_count - 1)
    result = numpy.zeros((row_count, permutations_count))
    for i, (divident, divider) in enumerate(permutations(range(col_count), 2)):
        result[:,i] = data[:,divident] / data[:,divider]
    return result


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())

