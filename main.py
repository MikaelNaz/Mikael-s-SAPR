from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QTableView, QVBoxLayout, QApplication, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QPen, QColor, QBrush, QPainter, QStandardItem
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from window import Ui_MainWindow
import sys
import os
import re
import numpy as np
# import cv2

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tableView(self.ui.tableView, ["Площадь сечения", "Длина", "Модуль упругости", "Напряжение", "Первый узел", "Сосредоточенные силы", "Распределенные нагрузки"], self.ui.add_1, self.ui.delete_1)
        self.ui.save_1.clicked.connect(self.save_table_data)
        self.ui.save_3.clicked.connect(self.check_table_data)
        self.ui.opora_left.stateChanged.connect(self.get_opora_left)
        self.ui.opora_right.stateChanged.connect(self.get_opora_right)
        self.ui.draw_button.clicked.connect(self.draw_rectangles)
        self.ui.draw_button_2.clicked.connect(self.draw_diagrams)
        self.ui.graphicsView.setScene(QtWidgets.QGraphicsScene())
        self.ui.graphicsView_2.setScene(QtWidgets.QGraphicsScene())
        self.ui.graphicsView_3.setScene(QtWidgets.QGraphicsScene())
        self.ui.graphicsView_4.setScene(QtWidgets.QGraphicsScene())
        self.ui.open_1.clicked.connect(self.open_table_data)
        self.ui.action_5.triggered.connect(self.close)
        self.ui.processor.clicked.connect(self.processor)
        self.ui.tableView.setColumnWidth(5, 150)
        self.ui.tableView.setColumnWidth(6, 200)
        self.opora_right_exists = False
        self.opora_left_exists = False
        self.tableView_2(self.ui.tableView_2, ["Данные", "Результат"])
        self.ui.tableView_2.setColumnWidth(0, 495)
        self.ui.tableView_2.setColumnWidth(1, 495)
        self.point_line()
        self.ui.get_point.clicked.connect(self.get_point_values)

    def wheelEvent(self, event):
        current_scale = self.ui.graphicsView.transform().m11()  # Получаем текущий масштаб вида
        if event.angleDelta().y() > 0: # Изменяем масштаб в зависимости от направления поворота колесика мыши
            factor = 1.1
        else:
            factor = 0.9
        self.ui.graphicsView.scale(factor, factor)     # Устанавливаем новый масштаб вида

    def tableView(self, tableView, headers, addButton, deleteButton):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        tableView.setModel(model)
        addButton.clicked.connect(lambda: self.add_row(model))
        deleteButton.clicked.connect(lambda: self.delete_rows(tableView, model))

    def tableView_2(self, tableView, headers):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        tableView.setModel(model)

    def add_row(self, model):
        row = [QtGui.QStandardItem("") for _ in range(model.columnCount())]
        model.appendRow(row)

    def delete_rows(self, tableView, model):
        indexes = tableView.selectionModel().selectedRows()
        for index in sorted(indexes, reverse=True):
            model.removeRow(index.row())

    def get_table_data(self, tableView):
        model = tableView.model()
        data = []
        for row in range(model.rowCount()):
            row_data = []
            for column in range(model.columnCount()):
                item = model.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            data.append(row_data)
        return data

    def save_table_data(self):
        data = self.get_table_data(self.ui.tableView)
        filename, _ = QFileDialog.getSaveFileName(self, "Save CN File", "", "Text Files (*.txt)")
        if filename:
            supports = {
                'opora_left': self.ui.opora_left.isChecked(),
                'opora_right': self.ui.opora_right.isChecked()
            }
            with open(filename, "w") as file:
                # Запись состояния опор в файл
                support_line = "{}\t{}".format(supports['opora_left'], supports['opora_right'])
                file.write(support_line + "\n")

                # Запись данных из таблицы
                for row in data:
                    for value in row:
                        if not re.match(r'^-?\d+(\.\d+)?$', value):
                            QtWidgets.QMessageBox.critical(self, "Error", "Invalid value: " + value)
                            return
                    file.write("\t".join(row) + "\n")

    def open_table_data(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open CN File", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "r") as file:
                data = []
                supports_line = file.readline().strip()
                supports = supports_line.split("\t")
                self.ui.opora_left.setChecked(supports[0] == 'True')
                self.ui.opora_right.setChecked(supports[1] == 'True')

                for line in file:
                    row = line.strip().split("\t")
                    data.append(row)
                self.set_table_data(data, self.ui.tableView,
                                    ["Площадь сечения", "Длина", "Модуль упругости", "Напряжение", "Первый узел",
                                     "Сосредоточенные силы", "Распределенные нагрузки"], self.ui.add_1,
                                    self.ui.delete_1)
                QtWidgets.QMessageBox.information(self, "Success", "CN data opened successfully!")

    def set_table_data(self, data, tableView , headers, addButton, deleteButton):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)
        for row in data:
            item_row = []
            for value in row:
                item = QStandardItem(value)
                item_row.append(item)
            model.appendRow(item_row)
        tableView.setModel(model)
        addButton.clicked.connect(lambda: self.add_row(model))
        deleteButton.clicked.connect(lambda: self.delete_rows(tableView, model))

    def get_opora_right(self, checked):
        if checked:
            self.opora_right_exists = True
        else:
            self.opora_right_exists = False

    def get_opora_left(self, checked):
        if checked:
            self.opora_left_exists = True
        else:
            self.opora_left_exists = False

    def check_table_data(self):
        try:
            data = self.get_table_data(self.ui.tableView)
            if len(data) == 0:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Задайте конструкцию! 😊")
                return
            pattern = r'^-?\d+(\.\d+)?$'
            for row in data:
                for value in row:
                    if float(row[0]) <= 0:
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Площадь сечения не может быть равна: " + row[0])
                        return
                    if float(row[1]) <= 0:
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Длина не может быть равна: " + row[1])
                        return
                    if float(row[2]) <= 0:
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Модуль упругости не может быть равен: " + row[2])
                        return
                    if float(row[3]) <= 0:
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Напряжение не может быть равно: " + row[3])
                        return
                    if not re.match(pattern, value):
                        QtWidgets.QMessageBox.critical(self, "Error", "Invalid value: " + value)
                        return
            if self.opora_right_exists == False and self.opora_left_exists == False:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Не заданы опоры! 🥱")
                return
            QtWidgets.QMessageBox.information(self, "Success", "Table data is valid!")

        except Exception:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Заполните таблицу до конца 😎")

    def draw_rectangles(self):
        try:
            data = self.get_table_data(self.ui.tableView)
            if len(data) == 0:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Задайте конструкцию! 🙃")
                return
            if self.opora_right_exists == False and self.opora_left_exists == False:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Не заданы опоры! 🥱")
                return
            self.ui.graphicsView.scene().clear()

            total_width = 0
            for row in data:
                length = float(row[1])
                total_width += length

            x = self.ui.graphicsView.width() / 2 - total_width / 2
            y = self.ui.graphicsView.height() / 2
            koef_1 = (-x) + (total_width / 4)

            for row in (data):
                area = float(row[0])  # Area y
                length = float(row[1])  # Length x
                concentrated_forces = float(row[5]) # сосредоточенные силы
                distributed_forces = float(row[6]) # распределенные силы
                if float(row[0]) <= 0:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Площадь сечения не может быть равна: " + row[0])
                    return
                if float(row[1]) <= 0:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Длина не может быть равна: " + row[1])
                    return
                if float(row[2]) <= 0:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Модуль упругости не может быть равен: " + row[2])
                    return
                if float(row[3]) <= 0:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Напряжение не может быть равно: " + row[3])
                    return

                length = length * 100
                area = area * 100
                rectangle = QtWidgets.QGraphicsRectItem(x, y - area / 2, length, area)
                pen = QtGui.QPen()
                pen.setColor(QtGui.QColor(0, 0, 0))
                pen.setWidth(5)
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                rectangle.setPen(pen)
                rectangle.setBrush(brush)

                # Рисование распределенной силы всех узлов, кроме первого
                if distributed_forces >= 1:
                    koe = x
                    for i in range(int(length // 20)):    # количество стрелок
                        pen = QtGui.QPen()
                        pen.setColor(QtGui.QColor(0, 0, 255))
                        line_three_0 = QtWidgets.QGraphicsLineItem(koe, y, koe + 10, y)
                        line_three_1 = QtWidgets.QGraphicsLineItem(koe + 10, y, koe + 5, y - 3)
                        line_three_2 = QtWidgets.QGraphicsLineItem(koe + 10, y, koe + 5, y + 3)
                        line_three_0.setPen(pen)
                        line_three_1.setPen(pen)
                        line_three_2.setPen(pen)
                        line_three_0.setZValue(1)  # Отрисовка поверх уже существующих
                        line_three_1.setZValue(1)
                        line_three_2.setZValue(1)
                        pen.setWidth(3)
                        self.ui.graphicsView.scene().addItem((line_three_0))
                        self.ui.graphicsView.scene().addItem((line_three_1))
                        self.ui.graphicsView.scene().addItem((line_three_2))
                        koe += 20
                    koe = x
                elif distributed_forces < 0:
                    koe = x
                    for i in range(int(length // 20)):
                        pen = QtGui.QPen()
                        pen.setColor(QtGui.QColor(255, 0, 0))
                        pen.setWidth(1)
                        line_three_0 = QtWidgets.QGraphicsLineItem(koe, y, koe + 10, y)
                        line_three_1 = QtWidgets.QGraphicsLineItem(koe , y, koe + 5, y - 3)
                        line_three_2 = QtWidgets.QGraphicsLineItem(koe , y, koe + 5, y + 3)
                        line_three_0.setPen(pen)
                        line_three_1.setPen(pen)
                        line_three_2.setPen(pen)
                        line_three_0.setZValue(1)
                        line_three_1.setZValue(1)
                        line_three_2.setZValue(1)
                        self.ui.graphicsView.scene().addItem((line_three_0))
                        self.ui.graphicsView.scene().addItem((line_three_1))
                        self.ui.graphicsView.scene().addItem((line_three_2))
                        koe += 20
                    koe = x

                # Рисование сосредоточенной силы всех узлов, кроме первого
                if concentrated_forces >= 1:
                    print(concentrated_forces)
                    koef = x + length
                    pen = QtGui.QPen()
                    pen.setColor(QtGui.QColor(0, 0, 255))
                    pen.setWidth(3)
                    line_one_0 = QtWidgets.QGraphicsLineItem(koef, y, koef + 25, y)
                    line_one_1 = QtWidgets.QGraphicsLineItem(koef + 25, y, koef + 20, y - 5)
                    line_one_2 = QtWidgets.QGraphicsLineItem(koef + 25, y, koef + 20, y + 5)
                    line_one_0.setPen(pen)
                    line_one_1.setPen(pen)
                    line_one_2.setPen(pen)
                    line_one_0.setZValue(1)
                    line_one_1.setZValue(1)
                    line_one_2.setZValue(1)
                    self.ui.graphicsView.scene().addItem((line_one_0))
                    self.ui.graphicsView.scene().addItem((line_one_1))
                    self.ui.graphicsView.scene().addItem((line_one_2))
                elif concentrated_forces < 0:
                    koef = x + length
                    pen = QtGui.QPen()
                    pen.setColor(QtGui.QColor(255, 0, 0))
                    pen.setWidth(3)
                    line_one_0 = QtWidgets.QGraphicsLineItem(koef, y, koef - 25, y)
                    line_one_1 = QtWidgets.QGraphicsLineItem(koef - 25, y, koef - 20, y - 5)
                    line_one_2 = QtWidgets.QGraphicsLineItem(koef - 25, y, koef - 20, y + 5)
                    line_one_0.setPen(pen)
                    line_one_1.setPen(pen)
                    line_one_2.setPen(pen)
                    line_one_0.setZValue(1)
                    line_one_1.setZValue(1)
                    line_one_2.setZValue(1)
                    self.ui.graphicsView.scene().addItem((line_one_0))
                    self.ui.graphicsView.scene().addItem((line_one_1))
                    self.ui.graphicsView.scene().addItem((line_one_2))

                self.ui.graphicsView.scene().addItem(rectangle)
                x += length
                x_last_opora = x

            # Правая опора
            if self.opora_right_exists == True:
                print(self.opora_right_exists)
                y = self.ui.graphicsView.height() / 2
                pen = QtGui.QPen()
                pen.setColor(QtGui.QColor(0, 0, 0))
                pen.setWidth(2)
                post_koef_1 = y - (area // 2) - 30
                post_koef_2 = y + (area // 2) + 30
                line_five_0 = QtWidgets.QGraphicsLineItem(x_last_opora, post_koef_1 , x_last_opora, post_koef_2)
                line_five_0.setPen(pen)
                line_five_0.setZValue(1)
                self.ui.graphicsView.scene().addItem((line_five_0))
                numbers = (area + 60) // 10 # количество прямых под углом
                for i in range (int(numbers)):
                    line_five_1 = QtWidgets.QGraphicsLineItem(x_last_opora, post_koef_1, x_last_opora + 10, post_koef_1 - 10)
                    line_five_1.setPen(pen)
                    line_five_1.setZValue(1)
                    post_koef_1 += 10
                    self.ui.graphicsView.scene().addItem((line_five_1))

            # Левая опора
            if self.opora_left_exists == True:
                print(self.opora_left_exists)
                x = self.ui.graphicsView.width() / 2 - total_width / 2
                y = self.ui.graphicsView.height() / 2
                pen = QtGui.QPen()
                pen.setColor(QtGui.QColor(0, 0, 0))
                pen.setWidth(2)
                post_koef_1 = y - (area // 2) - 30
                post_koef_2 = y + (area // 2) + 30
                line_four_0 = QtWidgets.QGraphicsLineItem(x, post_koef_1 , x, post_koef_2)
                line_four_0.setPen(pen)
                line_four_0.setZValue(1)
                self.ui.graphicsView.scene().addItem((line_four_0))
                numbers = (area + 60) // 10 # количество прямых под углом
                for i in range (int(numbers)):
                    line_four_1 = QtWidgets.QGraphicsLineItem(x, post_koef_1, x - 10 , post_koef_1 + 10)
                    line_four_1.setPen(pen)
                    line_four_1.setZValue(1)
                    post_koef_1 += 10
                    self.ui.graphicsView.scene().addItem((line_four_1))

                #Рисование сосредоточенной силы первого узла
            first_node = float(data[0][4])
            if first_node >= 1:
                x = self.ui.graphicsView.width() / 2 - total_width / 2
                y = self.ui.graphicsView.height() / 2
                pen = QtGui.QPen()
                pen.setColor(QtGui.QColor(0, 0, 255))
                pen.setWidth(3)
                line_two_0 = QtWidgets.QGraphicsLineItem(x, y, x + 25, y)
                line_two_1 = QtWidgets.QGraphicsLineItem(x + 25, y, x + 20 , y - 5)
                line_two_2 = QtWidgets.QGraphicsLineItem(x + 25, y, x + 20, y + 5)
                line_two_0.setPen(pen)
                line_two_1.setPen(pen)
                line_two_2.setPen(pen)
                line_two_0.setZValue(1)
                line_two_1.setZValue(1)
                line_two_2.setZValue(1)
                self.ui.graphicsView.scene().addItem((line_two_0))
                self.ui.graphicsView.scene().addItem((line_two_1))
                self.ui.graphicsView.scene().addItem((line_two_2))
            elif first_node < 0:
                x = self.ui.graphicsView.width() / 2 - total_width / 2
                y = self.ui.graphicsView.height() / 2
                pen = QtGui.QPen()
                pen.setColor(QtGui.QColor(255, 0, 0))
                pen.setWidth(3)
                line_two_0 = QtWidgets.QGraphicsLineItem(x, y, x - 25 , y)
                line_two_1 = QtWidgets.QGraphicsLineItem(x - 25, y, x - 20, y - 5)
                line_two_2 = QtWidgets.QGraphicsLineItem(x - 25, y, x - 20, y + 5)
                line_two_0.setPen(pen)
                line_two_1.setPen(pen)
                line_two_2.setPen(pen)
                pen.setWidth(10)
                self.ui.graphicsView.scene().addItem((line_two_0))
                self.ui.graphicsView.scene().addItem((line_two_1))
                self.ui.graphicsView.scene().addItem((line_two_2))

        except Exception:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Вы меня не сломаете 🚀")

    # Матрица реакций
    def matrix(self):
        data = self.get_table_data(self.ui.tableView)
        count = len(data) + 1
        A = [[0] * count for _ in range(count)]

        for i in range(len(data)):
            area = float(data[i][0])
            length = float(data[i][1])
            module = float(data[i][2])

            k = (module * area) / length
            A[i][i] += k
            A[i + 1][i + 1] += k
            A[i][i + 1] -= k
            A[i + 1][i] -= k

        if self.opora_left_exists == True:
            A[0][0] = 1
            A[1][0] = 0
            A[0][1] = 0

        if self.opora_right_exists == True:
            A[count - 1][count - 1] = 1
            A[count - 1][count - 2] = 0
            A[count - 2][count - 1] = 0
        return A

    # Верно
    def delta(self):
        data = self.get_table_data(self.ui.tableView)
        count = len(data) + 1
        B = [0] * count
        last_concentrated_forces = 0
        for i in range(len(data)):
            length = float(data[i][1])
            module = float(data[i][2])
            voltage = float(data[i][3])
            first_node = float(data[0][4])
            concentrated_forces = float(data[i][5])  # сосредоточенные силы
            distributed_forces = float(data[i][6])  # распределенные силы

            B[i] += ((distributed_forces  * length) / 2) + first_node + last_concentrated_forces
            last_concentrated_forces = concentrated_forces
            B[i+1] += ((distributed_forces  * length) / 2)

        B[count - 1] += last_concentrated_forces

        if self.opora_left_exists == True:  # Если левая опора существует и это первая итерация
            B[0] = 0
        if self.opora_right_exists == True:  # Если правая опора существует и это последняя итерация
            B[count - 1] = 0
        # print("\nГлобальный вектор реакций b:", B)
        return B


    # Верно
    def vector_delta(self):
        data = self.get_table_data(self.ui.tableView)
        count = len(data) + 1
        A = self.matrix()
        B = self.delta()
        try:
            A = np.linalg.inv(A)
        except:
            np.linalg.lstsq(A, A)
        sum = np.dot(A, B)
        # print("\nГлобальный вектор перемещений Δ:", sum)
        return sum

    def longitudinal_N(self):                             #продольные силы
        data = self.get_table_data(self.ui.tableView)
        count = len(data)
        sum = self.vector_delta()
        point_count = 100
        N = np.zeros((count, point_count))
        # N = np.zeros((count, 2))

        for i in range(len(data)):
            area = float(data[i][0])
            length = float(data[i][1])
            module = float(data[i][2])
            voltage = float(data[i][3])
            first_node = float(data[0][4])
            concentrated_forces = float(data[i][5])  # сосредоточенные силы
            distributed_forces = float(data[i][6])  # распределенные силы
            # a = (sum[i + 1] - sum[i])
            #
            # N[i][0] = ((module * area) / length) * a + ((distributed_forces * voltage * length) / 2) * (1 - ((2 * 0) / length))
            # N[i][1] = ((module * area) / length) * a + ((distributed_forces * voltage * length) / 2) * (1 - ((2 * length) / length))
            #
            # if distributed_forces == 0:
            #     N[i][0] = ((module * area) / length) * a
            #     N[i][1] = ((module * area) / length) * a
            for j in range(0, point_count):
                a = (sum[i+1] - sum[i])
                N[i][j] = ((module * area) / length) * a + ((distributed_forces * voltage * length) / 2) * (1 - ((2 * j) / (point_count - 1)))
        return N

    def normal_voltage(self):                                    # нормальное напряжение
        data = self.get_table_data(self.ui.tableView)
        count = len(data)
        longitudinal_N = self.longitudinal_N()
        for i in range(len(data)):
            area = float(data[i][0])
            longitudinal_N[i] /= area
            longitudinal_N[i] /= area
        # print("\nНормальное напряжение σ: ", longitudinal_N)
        return longitudinal_N

    def movements_U(self):                                    # перемещения
        data = self.get_table_data(self.ui.tableView)
        count = len(data)
        A = self.matrix()
        B = self.delta()
        sum = self.vector_delta()
        point_count = 100
        U = np.zeros((count, point_count))
        # U = np.zeros((count, 2))

        for i in range(len(data)):
            area = float(data[i][0])
            length = float(data[i][1])
            module = float(data[i][2])
            voltage = float(data[i][3])
            first_node = float(data[0][4])
            concentrated_forces = float(data[i][5])  # сосредоточенные силы
            distributed_forces = float(data[i][6])  # распределенные силы

            # a = (sum[i + 1] - sum[i])
            # U[i][0] = sum[i] + (0 / length) * (sum[i + 1] - sum[i]) + ((distributed_forces * voltage * (length ** 2) * 0) / (2 * module * area * length)) * (1 - (0 / length))
            # U[i][1] = sum[i] + (length / length) * (sum[i + 1] - sum[i]) + ((distributed_forces * voltage * (length ** 2) * length) / (2 * module * area * length)) * (1 - (length / length))
            #
            # if distributed_forces == 0:
            #     U[i][0] = sum[i] + (0 / length) * (sum[i + 1] - sum[i])
            #     U[i][1] = sum[i] + (length / length) * (sum[i + 1] - sum[i])

            for j in range(0, point_count):
                a = (sum[i+1] - sum[i])
                U[i][j] = sum[i] + (j / (point_count - 1)) * (sum[i + 1] - sum[i]) + (
                            (distributed_forces * voltage * (length ** 2) * j) / (2 * module * area * length)) * (
                                      1 - (j / (point_count - 1)))
        return U

    def processor(self):
        try:
            data = self.get_table_data(self.ui.tableView)
            if len(data) == 0:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Задайте конструкцию! 🙃")
                return

            if self.opora_right_exists == False and self.opora_left_exists == False:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Не заданы опоры! 🥱")
                return

            for i in range(len(data)):
                voltage = float(data[i][3])

            A = self.matrix()
            B = self.delta()
            SUM = self.vector_delta()
            N = self.longitudinal_N()
            S = self.normal_voltage()
            U = self.movements_U()

            if A == [[0]]:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Вы меня, возможно, никогда не сломаете 😊")
            else:
                print('Матрица реакций A: ', A)
                print("\nГлобальный вектор реакций b:", B)
                print("\nГлобальный вектор перемещений Δ:", SUM)
                print("\nПеремещения N: ", N)
                print("\nНормальные напряжения σ: ", S)
                print("\nПеремещения U: ", U)

                table_data = []
                for i in range(len(N)):
                    table_data.append(["Продольные силы N[{}]".format(i + 1), (N[i][0], N[i][-1])])
                for i in range(len(S)):
                    table_data.append(["Нормальные напряжения σ[{}]".format(i + 1), (S[i][0], S[i][-1])])
                for i in range(len(U)):
                    table_data.append(["Перемещения U[{}]".format(i + 1), (U[i][0], U[i][-1])])

                model = self.ui.tableView_2.model()
                model.removeRows(0, model.rowCount())
                model.setRowCount(len(table_data))
                for row, data in enumerate(table_data):
                    header = data[0]
                    values = ', '.join(map(str, data[1:]))
                    model.setData(model.index(row, 0), header, Qt.DisplayRole)
                    model.setData(model.index(row, 1), values, Qt.DisplayRole)
                    if header.startswith("Нормальные напряжения σ"):
                        for i in range(len(S)):
                            if S[i][0] > voltage:
                                model.setData(model.index(row + i, 1), QBrush(QColor("red")), Qt.BackgroundRole)
                            if S[i][-1] > voltage:
                                model.setData(model.index(row + i, 1), QBrush(QColor("red")), Qt.BackgroundRole)

                with open('results.txt', 'w', encoding='utf-8') as file:
                    file.write('Матрица реакций A: {}\n'.format(A))
                    file.write('Глобальный вектор реакций b: {}\n'.format(B))
                    file.write('Глобальный вектор перемещений Δ: {}\n'.format(SUM))
                    file.write('Результаты расчетов:\n')
                    for row, (header, value) in enumerate(table_data):
                        file.write('{}: {}\n'.format(header, value))

                QtWidgets.QMessageBox.information(self, "Sucess", "Результаты расчетов записаны в файл results.txt")

        except Exception:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Вы меня почти сломали, но я выдержал этот натиск 😎")

    # def draw_diagrams(self): # проверка на работоспособность
    #     # x = [-1, -2, -3, 4, 5, 6, 7, 8, 9, 10]
    #     # y = [-30, -32, -34, -32, -33, -31, -29, 32, 35, 45]
    #     x = [0, 2]
    #     y =[-1, -5]
    #
    #     scene = QtWidgets.QGraphicsScene()
    #     plot_widget = pg.PlotWidget()
    #     plot_widget.setBackground('w')
    #     plot_widget.plot(x, y, pen=pg.mkPen('b', width=2))
    #
    #     scene.addWidget(plot_widget)
    #     self.ui.graphicsView_2.setScene(scene)

    def draw_n(self):
        data = self.get_table_data(self.ui.tableView)
        x_start = 0
        N = self.longitudinal_N()

        scene = QtWidgets.QGraphicsScene()
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('w')

        i = 0
        for row in data:
            length = float(row[1])
            x = np.linspace(x_start, x_start + length, len(N[i]))
            y = N[i]
            plot_widget.plot(x, y, pen=pg.mkPen('b', width=2))
            # Прямая для разграничения
            vline = pg.InfiniteLine(pos=x_start + length, angle=90, movable=False)
            plot_widget.addItem(vline)
            x_start += length
            i += 1

        vline_1 = pg.InfiniteLine(pos=0, angle=90, movable=False)
        plot_widget.addItem(vline_1)

        scene.addWidget(plot_widget)
        return self.ui.graphicsView_2.setScene(scene)

    def draw_u(self):
        data = self.get_table_data(self.ui.tableView)
        x_start = 0
        U = self.movements_U()

        scene = QtWidgets.QGraphicsScene()
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('w')

        i = 0
        for row in data:
            length = float(row[1])
            x = np.linspace(x_start, x_start + length, len(U[i]))
            y = U[i]
            plot_widget.plot(x, y, pen=pg.mkPen('b', width=2))
            # Прямая для отделения
            vline = pg.InfiniteLine(pos=x_start + length, angle=90, movable=False)
            plot_widget.addItem(vline)
            x_start += length
            i += 1

        vline_1 = pg.InfiniteLine(pos=0, angle=90, movable=False)
        plot_widget.addItem(vline_1)

        scene.addWidget(plot_widget)
        self.ui.graphicsView_3.setScene(scene)

    def draw_s(self):
        data = self.get_table_data(self.ui.tableView)
        x_start = 0
        S = self.normal_voltage()

        scene = QtWidgets.QGraphicsScene()
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('w')

        i = 0
        for row in data:
            length = float(row[1])
            x = np.linspace(x_start, x_start + length, len(S[i]))
            y = S[i]
            plot_widget.plot(x, y, pen=pg.mkPen('b', width=2))
            # Прямая для отделения
            vline = pg.InfiniteLine(pos=x_start + length, angle=90, movable=False)
            plot_widget.addItem(vline)
            x_start += length
            i += 1

        vline_1 = pg.InfiniteLine(pos=0, angle=90, movable=False)
        plot_widget.addItem(vline_1)

        scene.addWidget(plot_widget)
        self.ui.graphicsView_4.setScene(scene)

    def draw_diagrams(self):
        data = self.get_table_data(self.ui.tableView)
        if len(data) == 0:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Задайте конструкцию! 🙃")
            return
        if self.opora_right_exists == False and self.opora_left_exists == False:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Не заданы опоры! 🥱")
            return
        try:
            N = self.draw_n()
            U = self.draw_u()
            S = self.draw_s()
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Вы меня почти сломали, но я не поддамся 🎈")

    def get_point_values(self):
        input_text = self.ui.lineEdit.text()
        numbers = input_text.replace(" ", "").split(",")

        if len(numbers) != 2:
            self.ui.result_label.setText("Некорректный ввод")
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Некорректный ввод")
            return

        try:
            iteration = int(numbers[0])
            x = float(numbers[1])

            data = self.get_table_data(self.ui.tableView)
            count = len(data)
            print(count)
            sum = self.vector_delta()
            N = np.zeros((count, 1))
            U = np.zeros((count, 1))
            S = np.zeros((count, 1))
            k = 1

            # Проверка на положительность итерации
            if iteration <= 0 or iteration > count:
                self.ui.result_label.setText("Некорректное значение стержня 😲")
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Некорректное значение стержня 😲")
                return

            for i in range(len(data)):
                area = float(data[i][0])
                length = float(data[i][1])
                module = float(data[i][2])
                voltage = float(data[i][3])
                first_node = float(data[0][4])
                concentrated_forces = float(data[i][5])
                distributed_forces = float(data[i][6])
                a = sum[i + 1] - sum[i]
                N = ((module * area) / length) * a + ((distributed_forces * voltage * length) / 2) * (
                        1 - ((2 * x) / length))
                U = sum[i] + (x / length) * (sum[i + 1] - sum[i]) + (
                        (distributed_forces * voltage * (length ** 2) * x) / (2 * module * area * length)) * (
                            1 - (x / length))
                S = N / area

                if distributed_forces == 0:
                    N = ((module * area) / length) * a
                    U = sum[i] + (0 / length) * (sum[i + 1] - sum[i])
                    S = N / area

                if k == iteration:
                    break
                else:
                    k += 1

            if x < 0 or x > length:
                self.ui.result_label.setText("Некорректное значение длины 😳")
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Некорректное значение длины 😳")
                return

            result = f"N: {str(N)}" + "\t" + f"σ: {str(S)}" + "\t" + f"U: {str(U)}"
            self.ui.result_label.setText(result)

        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Я выиграл эту схватку 🎄")

    def point_line(self):
        self.ui.lineEdit.setPlaceholderText("Пример: 1, 1")
        self.ui.lineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)

    def increase(self):
        QtWidgets.QMessageBox.critical(self, "Ошибка", "Я не хочу работать")

    def decrease(self):
        QtWidgets.QMessageBox.critical(self, "Ошибка", "Я тоже не хочу работать")

    def close(self):
        quit()

def create_app():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()

    win.show()
    sys.exit(app.exec_())

create_app()