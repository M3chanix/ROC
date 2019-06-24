import sys
import os
import sqlite3 as sql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QFileDialog, QComboBox, QPushButton, \
    QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QInputDialog, QDialog, QCheckBox, QHBoxLayout
os.chdir("C://py1")


def parse_file(fname):
    file = pd.read_excel(fname, skiprows=0)
    file = file.dropna(axis=0, how='all')
    unique_ids = file["Sample"].unique()

    # todo: в реальных данных индексы не должны совподать, поэтому строчка с дублированием лишняя
    # unique_ids = np.append(unique_ids, unique_ids)

    Cq = file["Cq"].to_numpy()
    miRNA_count = int(len(file)/len(unique_ids))
    Cq.resize(len(unique_ids), miRNA_count)
    labels = file["miRNA"].unique()
    patient_table = pd.DataFrame(Cq, columns=labels)
    patient_table.insert(0, "Sample", unique_ids)
    tissue = np.array([])
    for i in range(int(len(unique_ids))):
        # todo: сделать обработку случайного числа микрорнк, а не 24
        tissue = np.append(tissue, file["Tissue"].iloc[miRNA_count*i])

    return(unique_ids, tissue, patient_table)


def save_to_sql(data):
    connection = sql.connect("C:/py1/db1.db")
    data.to_sql("Patient_data", connection, if_exists="append", index=False)
    connection.close()


def read_from_sql(script):
    connection = sql.connect("C:/py1/db1.db")
    sql_data = pd.read_sql(script, connection)
    connection.close()

    return sql_data


class SavedDataWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def get_sql_lables(self):
        self.sql_lable_values = {}
        connection = sql.connect("C:/py1/db1.db")
        cursor = connection.cursor()
        query_part1 = "select distinct "
        query_part2 = " from Patient_data"
        for label in self.sql_labels:
            query = query_part1+label+query_part2
            cursor.execute(query)
            self.sql_lable_values[label] = cursor.fetchall()

        cursor.close()
        connection.close()

    def getSearcResults(self):
        script = """
        Select * From Patient_data
        """

        queryValues = []
        for i in (0, 7, 8):
            current_value = self.searchWidget.cellWidget(0, i).text()
            if current_value != "":
                queryValues.append('{} = "{}"'.format(self.table_labels[i], current_value))

        for i in range(1, 7, 1):
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
        self.resultWidget.setRowCount(len(self.sql_data))

        for i in range(len(self.sql_data)):
            for j in range(len(self.table_labels)):
                a = QLabel()
                a.setText(self.sql_data.iloc[i, j])
                self.resultWidget.setCellWidget(i, j, a)
        self.resultWidget.resizeColumnsToContents()
        self.sql_data = self.sql_data.dropna(axis=1, how="all")

    def prepareAnalyzis(self):
        results_widget = ResultsWindow()
        results_widget.initUI(self.sql_data)
        main_window.setCentralWidget(results_widget)

    def createSearchWidget(self):
        self.table_labels = ["Sample", "Tissue", "BIN_Diagnosis", "Source", "Material", "Operator_RNA_Isolation",
                             "Operator_PCR", "RNA_Concentration", "Diagnosis"]
        self.sql_labels = ["Tissue", "BIN_Diagnosis", "Source", "Material", "Operator_RNA_Isolation",
                             "Operator_PCR"]
        self.searchWidget.setColumnCount(len(self.table_labels))
        self.resultWidget.setColumnCount(len(self.table_labels))
        self.searchWidget.setHorizontalHeaderLabels(self.table_labels)
        self.resultWidget.setHorizontalHeaderLabels(self.table_labels)
        self.get_sql_lables()
        self.searchWidget.setRowCount(1)

        for key, j in zip(self.sql_labels, range(len(self.sql_labels))):
            a = QComboBox()
            a.addItem("Any")
            for label in self.sql_lable_values[key]:
                a.addItem(label[0])
            self.searchWidget.setCellWidget(0, j+1, a)

        for i in (0, 7, 8):
            a = QLineEdit()
            self.searchWidget.setCellWidget(0, i, a)
        self.searchWidget.resizeColumnsToContents()


    def initUI(self):
        self.setWindowTitle("TableWidget Test")
        self.grid_layout = QGridLayout()
        self.searchWidget = QTableWidget()
        self.resultWidget = QTableWidget()

        self.TextLabel = QLabel("Поиск по базе")
        processSearchButton = QPushButton("Обработать")
        AnalyzeButton = QPushButton("Провести анализ")
        self.createSearchWidget()
        self.grid_layout.addWidget(self.TextLabel)
        self.grid_layout.addWidget(self.searchWidget)
        self.grid_layout.addWidget(processSearchButton)
        self.grid_layout.addWidget(self.resultWidget)
        self.grid_layout.addWidget(AnalyzeButton)

        processSearchButton.clicked.connect(self.getSearcResults)
        AnalyzeButton.clicked.connect(self.prepareAnalyzis)

        self.setLayout(self.grid_layout)
        self.setGeometry(300, 300, 930, 400)
        self.show()


class NewDataWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def createTableWidget(self):
        self.tableWidget.setColumnCount(9)
        self.table_labels = ["Sample", "Tissue", "BIN_Diagnosis", "Source", "Material", "Operator_RNA_Isolation",
             "Operator_PCR", "RNA_Concentration", "Diagnosis"]
        self.sql_labels = ["Source", "Material", "Operator_RNA_Isolation", "Operator_PCR"]
        self.tableWidget.setHorizontalHeaderLabels(self.table_labels)
        self.get_sql_lables()
        patient_ids, self.tissue_list, self.patient_table = parse_file(self.fname)
        self.tableWidget.setRowCount(len(patient_ids))

        for i in range(len(patient_ids)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(patient_ids[i]))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(self.tissue_list[i]))
            a = QComboBox()
            a.addItem("HSIL")
            a.addItem("LSIL")
            self.tableWidget.setCellWidget(i, 2, a)
            for key, j in zip(self.sql_labels, range(len(self.sql_labels))):
                a = QComboBox()
                for label in self.sql_lable_values[key]:
                    a.addItem(label[0])
                a.addItem("Add new...")
                a.activated.connect(self.addNewLabel)
                self.tableWidget.setCellWidget(i, j+3, a)
            self.tableWidget.setCellWidget(i, 7, QLineEdit())
            self.tableWidget.setCellWidget(i, 8, QLineEdit())
        self.tableWidget.resizeColumnsToContents()

    def initUI(self):

        self.grid_layout = QGridLayout()
        self.tableWidget = QTableWidget()

        fileButton = QPushButton("Выберите файл")
        self.fnameLabel = QLabel()
        processFileButton = QPushButton("Обработать")
        self.grid_layout.addWidget(fileButton)
        self.grid_layout.addWidget(self.fnameLabel)
        AnalyzeButton = QPushButton("Провести анализ")
        self.grid_layout.addWidget(processFileButton)
        self.grid_layout.addWidget(self.tableWidget)
        self.grid_layout.addWidget(AnalyzeButton)

        fileButton.clicked.connect(self.manageFile)
        processFileButton.clicked.connect(self.createTableWidget)
        AnalyzeButton.clicked.connect(self.prepareAnalyzis)

        self.setLayout(self.grid_layout)

    def manageFile(self):
        fname, type = QFileDialog.getOpenFileName()
        self.fnameLabel.setText("Выбранный файл: {}".format(fname))
        self.fname = fname

    def get_sql_lables(self):
        self.sql_lable_values = {}
        connection = sql.connect("C:/py1/db1.db")
        cursor = connection.cursor()
        query_part1 = "select distinct "
        query_part2 = " from Patient_data"
        for label in self.sql_labels:
            query = query_part1+label+query_part2
            cursor.execute(query)
            self.sql_lable_values[label] = cursor.fetchall()

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

    def prepareAnalyzis(self):
        additional_data_dict = {}
        # todo: заменить все дебильные костыли с range на нормальный синтаксис range(start, stop, step)
        for j in range(self.tableWidget.columnCount()-2):
            column_list = []
            for i in range(self.tableWidget.rowCount()):
                if j < 5:
                    column_list.append(self.tableWidget.cellWidget(i, j+2).currentText())
                else:
                    column_list.append(self.tableWidget.cellWidget(i, j+2).text())
            additional_data_dict[self.tableWidget.horizontalHeaderItem(j+2).text()] = column_list
        additional_data = pd.DataFrame(additional_data_dict)

        results_widget = ResultsWindow()

        for i, label in zip(range(len(additional_data.columns)), additional_data.columns):
            self.patient_table.insert(i+1, label, additional_data[label])
            # if i == 0:
            #     results_widget.initUI(self.patient_table)
        self.patient_table.insert(1, "Tissue", self.tissue_list)
        results_widget.initUI(self.patient_table)
        save_to_sql(self.patient_table)
        main_window.setCentralWidget(results_widget)


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
        self.hboxLayout = QHBoxLayout()
        SavedDataButton = QPushButton("Использовать данные из базы")
        NewDataButton = QPushButton("Внести новые данные из файла")
        self.hboxLayout.addWidget(SavedDataButton)
        self.hboxLayout.addWidget(NewDataButton)
        NewDataButton.clicked.connect(self.NewDataClicked)
        SavedDataButton.clicked.connect(self.SavedDataClicked)
        self.setLayout(self.hboxLayout)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("MainWindow")
        self.setGeometry(300, 200, 1030, 450)
        first_window = FirstWindow()
        # new_data_window = NewDataWindow()
        self.setCentralWidget(first_window)
        self.show()


class ResultsWindow(QWidget):

    def __init__(self):
        super().__init__()
        # self.initUI()

    def initUI(self, raw_data):
        norm_data = self.normalization(raw_data)
        self.fpr, self.tpr, self.threshold, self.roc_auc = self.roc_analyze(norm_data)
        roc_list = self.sort_dictionary_by_value(self.roc_auc)
        # self.draw_roc_curve(fpr, tpr, roc_auc, norm_data.columns[2:5])

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
        column_names = list(raw_data)
        norm_data = pd.DataFrame(raw_data, columns=raw_data.columns[:9])
        for divident in column_names[9:]:
            for divider in column_names[9:]:
                if divident != divider:
                    norm_data[divident + '/' + divider] = raw_data[divident] / raw_data[divider]
        norm_data = norm_data.fillna(0)
        return norm_data

    def roc_analyze(self, norm_data):
        fpr = dict()
        tpr = dict()
        threshold = dict()
        roc_auc = dict()
        for i in norm_data.columns[9:]:
            fpr[i], tpr[i], threshold[i] = metrics.roc_curve(norm_data["BIN_Diagnosis"], norm_data[i], pos_label="HSIL")
            roc_auc[i] = metrics.auc(fpr[i], tpr[i])

        return fpr, tpr, threshold, roc_auc

    def sort_dictionary_by_value(self, dictionary):
        list_of_sorted_pairs = [(k, dictionary[k]) for k in sorted(dictionary.keys(), key=dictionary.get, reverse=True)]
        return list_of_sorted_pairs

    def draw_roc_curve(self, fpr, tpr, roc_auc, miRNA_names):
        plt.figure()
        for i in miRNA_names:
            plt.plot(fpr[i], tpr[i], label="{0}; auc={1:0.2f}".format(i, roc_auc[i]))
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC curve')
        plt.legend(loc="lower right")
        plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())

