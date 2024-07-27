import os
import sys
import argparse
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtWidgets import QFrame, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from bins.handle_pd import PD
from bins.txt_operation import ReadTxt2List
import json
from bins.historical.poke_window import RequestData,ProcessData

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        venv_path = os.path.dirname(os.getcwd())
        root_path = ''
        if '.venv' not in venv_path:
            root_path = os.getcwd()  # Get the current folder from the .venv/scripts/.
        else:
            root_path = os.path.dirname(os.path.dirname(os.getcwd()))  # Get the grandparent folder from the .venv/scripts/.
        self.resource_path = os.path.join(root_path, 'resources')
        
        with open(os.path.join(self.resource_path, "main_window.json"), "r") as file:
            config = json.load(file)
        
        self.setWindowTitle(config['window_title'])
        self.resize(config['main_window_width'], config['main_window_height'])  # Set initial window size
        self.setMinimumSize(config['main_window_min_width'], config['main_window_min_height'])  # Set minimum window size
        
        # Set window icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "resources/pds.ico")
        self.setWindowIcon(QIcon(icon_path))

        # Set taskbar icon
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)

        # Create labels and input fields
        self.flight_label = QLabel("Inbound / Outbound / In_Date / Out_Date / Inbound_Departure:  ")
        self.pd_label = QLabel('PD')
        self.pd_text = QLineEdit('')
        self.pd_text.setStyleSheet("border: none;")
        self.pending_time_text = QLineEdit(str(config['pending_time_value']))
        self.pending_time_text.setFixedWidth(25)
        self.pending_time_text.setStyleSheet("QLineEdit { background-color: #CCCCCC; color: #444444; border:none;}")
        self.flight_inout = QLineEdit(self)
        self.flight_inout.setText('983/984/01JUN/02JUN/PEK')
        self.flight_inout.setFixedWidth(config['QLineEdit_long_width'])
        self.flight_inout.setStyleSheet("border: none;")
        
        # Create button and QLineEdit for file path
        self.file_button = QPushButton("Open...")
        self.file_button.clicked.connect(self.open_file_dialog)

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setStyleSheet("border: none;")
        self.file_path_edit.setFixedWidth(config['QLineEdit_long_width'])

        # Create "Run" button
        self.run_button = QPushButton("Run")
        self.run_button.setFixedWidth(config['QLineEdit_short_width'])
        self.run_button.clicked.connect(lambda: self.run_logic())
        
        # Create 'Poke' button
        self.poke_button = QPushButton('Poke a Window')
        self.poke_button.setFixedWidth(config['QLineEdit_short_width'])
        self.poke_button.clicked.connect(lambda: self.poke_logic())

        # Create a QHBoxLayout for the rows
        first_row_layout = QHBoxLayout()
        first_row_left = QHBoxLayout()
        first_row_left.addWidget(self.flight_label)
        first_row_left.setAlignment(Qt.AlignmentFlag.AlignLeft)
        first_row_left.addStretch()
        first_row_right = QHBoxLayout()
        first_row_right.addWidget(self.pending_time_text)
        first_row_right.setAlignment(Qt.AlignmentFlag.AlignRight)
        first_row_layout.addLayout(first_row_left)
        first_row_layout.addLayout(first_row_right)

        second_row_layout = QHBoxLayout()
        second_row_layout.addWidget(self.flight_inout)
        second_row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        
        third_row_layout = QHBoxLayout()      
        third_row_left = QHBoxLayout()
        third_row_left.addWidget(self.pd_label)
        third_row_left.addWidget(self.pd_text)
        third_row_left.addStretch()  # Add stretch to push widgets to the left
        third_row_left.setAlignment(Qt.AlignmentFlag.AlignLeft)
        third_row_layout.addLayout(third_row_left)

        third_row_right = QHBoxLayout()
        third_row_right.addWidget(self.poke_button)
        third_row_right.setAlignment(Qt.AlignmentFlag.AlignRight)
        third_row_layout.addLayout(third_row_right)

        forth_row_layout = QHBoxLayout()
        forth_row_left = QHBoxLayout()
        forth_row_left.addWidget(self.file_path_edit)
        forth_row_left.addWidget(self.file_button)
        forth_row_left.setAlignment(Qt.AlignmentFlag.AlignLeft)
        forth_row_left.addStretch()
        forth_row_layout.addLayout(forth_row_left)
        forth_row_right = QHBoxLayout()
        forth_row_right.addWidget(self.run_button)
        forth_row_right.setAlignment(Qt.AlignmentFlag.AlignRight)
        forth_row_layout.addLayout(forth_row_right)

        # Create a QVBoxLayout for the main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(first_row_layout)
        main_layout.addLayout(second_row_layout)
        main_layout.addLayout(third_row_layout)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        main_layout.addLayout(forth_row_layout)
        
        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setStyleSheet('''
                            QMainWindow {
                            background-color: #CCCCCC;
                           }''')
        
    def showEvent(self, event):
        super().showEvent(event)
        self.flight_inout.setFocus()
        self.flight_inout.selectAll()
    
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        if file_path:
            self.file_path_edit.setText(file_path)

    def run_logic(self):
        file_path = self.file_path_edit.text()
        pd_text = ReadTxt2List(file_path)
        pd = PD(pd_text)
        name_list = pd.GetSameNames()
        seat_list = pd.GetSameSeats()
        msg_box = QMessageBox()
        msg_box.setWindowTitle('PD Messages')
        msg_text = ''
        if len(pd.ErrorMessage) != 0:
            msg_text += 'Messages:' + '\n'
            for line in pd.ErrorMessage:
                msg_text += line + '\n'
        if len(name_list) != 0:
            msg_text += 'Dup Names:' + '\n'
            for line in name_list:
                msg_text += line + '\n'
        if len(seat_list) != 0:
            msg_text += 'Dup Seats:' + '\n'
            for line in seat_list:
                msg_text += line + '\n'
        msg_box.setText(msg_text)
        msg_box.exec()

    def poke_logic(self):
        command_pending = float(self.pending_time_text.text())
        flight_info=self.flight_inout.text()
        pd_command='PD'+self.pd_text.text()
        if len(flight_info.split('/')) > 3:
            request_data=RequestData(self.resource_path, flight_info, command_pending)
            ProcessData(request_data.Commands)
        if len(pd_command) != 0:
            pass
        
def main():
    #parser = argparse.ArgumentParser(description="PD start")
    #parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    #args = parser.parse_args()

    # Create the application
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
