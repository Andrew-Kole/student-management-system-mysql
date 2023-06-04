from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QGridLayout, QMainWindow, \
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import mysql.connector
from dotenv import load_dotenv
import os
import typing

load_dotenv()
SCHOOL_HOST: typing.Final = os.getenv("SCHOOL_HOST")
SCHOOL_USER: typing.Final = os.getenv("SCHOOL_USER")
SCHOOL_PASSWORD: typing.Final = os.getenv("SCHOOL_PASSWORD")
SCHOOL_DATABASE: typing.Final = os.getenv("SCHOOL_DATABASE")


class DatabaseConnection:
    def __init__(self, host=SCHOOL_HOST, user=SCHOOL_USER, password=SCHOOL_PASSWORD, database=SCHOOL_DATABASE):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connection(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # Menubar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        search_menu_item.addAction(search_action)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Statusbar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Select cell detect
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.statusbar.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        cursor.close()
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        # Name line edit
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Courses combo box
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Mobile line edit
        self.student_mobile = QLineEdit()
        self.student_mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.student_mobile)

        # Submit button
        submit_button = QPushButton("Register")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.student_mobile.text()
        connection = DatabaseConnection().connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        sm_system.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText("Search")
        layout.addWidget(self.search_line_edit)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search(self):
        name = self.search_line_edit.text()
        connection = DatabaseConnection().connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name, ))
        result = cursor.fetchall()
        items = sm_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            sm_system.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        index = sm_system.table.currentRow()
        self.student_id = sm_system.table.item(index, 0).text()

        # Name line edit
        student_name = sm_system.table.item(index, 1).text()
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Courses combo box
        course_name = sm_system.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Mobile line edit
        student_mobile = sm_system.table.item(index, 3).text()
        self.student_mobile = QLineEdit(student_mobile)
        self.student_mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.student_mobile)

        # Submit button
        submit_button = QPushButton("Update")
        submit_button.clicked.connect(self.update_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.student_mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        sm_system.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        index = sm_system.table.currentRow()
        student_id = sm_system.table.item(index, 0).text()
        connection = DatabaseConnection().connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        sm_system.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully.")
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        It's an application for learning, that was done during a course.
        Feel free to critic it.
        """
        self.setText(content)


app = QApplication(sys.argv)
sm_system = MainWindow()
sm_system.show()
sm_system.load_data()
sys.exit(app.exec())
