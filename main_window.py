from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtWidgets import QFrame, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
import os
import yaml
import sys
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        venv_path = os.path.dirname(os.getcwd())
        root_path = ''
        # Get the Resource folder path.
        if '.venv' not in venv_path:
            root_path = os.getcwd()  # Get the current folder from the .venv/scripts/.
        else:
            root_path = os.path.dirname(os.path.dirname(os.getcwd()))  # Get the grandparent folder from the .venv/scripts/.
        self.resource_path = os.path.join(root_path, 'resources')
        # Get the setting.
        try:
            with open(os.path.join(self.resource_path, "main_window.yml"), "r") as file:
                setting_file= file.read()
            self.wnd_config=yaml.safe_load(setting_file)
        except FileNotFoundError as e:
            QMessageBox(f"The main window setting file is missing. {e}")
            return
        # Initialize the controls.
        self.setWindowTitle(self.wnd_config['window_title'])
        self.resize(self.wnd_config['main_window_width'], self.wnd_config['main_window_height'])  # Set initial window size
        self.setMinimumSize(self.wnd_config['main_window_min_width'], self.wnd_config['main_window_min_height'])  # Set minimum window size
        app_icon = QIcon(os.path.join(self.resource_path,'pd_star.ico'))
        self.setWindowIcon(app_icon)
        self.triggered_button = QPushButton(self.wnd_config['triggered_button_default_text'])
        self.triggered_button.setCheckable(True)
        self.triggered_button.clicked.connect(self.on_button_triggered)
        # Add Layout.
        main_layout=QVBoxLayout()
        first_row_layout = QHBoxLayout()
        first_row_layout.addWidget(self.triggered_button)
        main_layout.addLayout(first_row_layout)
        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setStyleSheet('''
                            QMainWindow {
                            background-color: #CCCCCC;
                           }''')
        
    def on_button_triggered(self):
        if self.triggered_button.isChecked():
            self.triggered_button.setText('Running')
        else:
            self.triggered_button.setText(self.wnd_config['triggered_button_default_text'])
        
def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()