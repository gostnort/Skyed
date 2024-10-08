from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox, QMenu
from PySide6.QtGui import QIcon
import os
import yaml
import sys
from ui_components import BriefingUI, CrewGenDecUI
from PySide6.QtCore import Qt
from bins.button_logic import ButtonLogic

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(5, 0, 5, 10)
        self.setup_window()
        self.create_menu_bar()
        self.setup_central_widget()
        self.button_logic = ButtonLogic()

    def setup_window(self):
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
                setting_file = file.read()
            self.wnd_config = yaml.safe_load(setting_file)
        except FileNotFoundError as e:
            QMessageBox.information(None, 'Error', f"The main window setting file is missing. {e}")
            return
        # Set up the main window
        self.setWindowTitle(self.wnd_config['window_title'])
        self.resize(self.wnd_config['main_window_width'], self.wnd_config['main_window_height'])
        self.setMinimumSize(self.wnd_config['main_window_min_width'], self.wnd_config['main_window_min_height'])
        app_icon = QIcon(os.path.join(self.resource_path, 'pd_star.ico'))
        self.setWindowIcon(app_icon)

        self.setStyleSheet(f'''
            QMainWindow {{ {self.wnd_config['stylesheets']['main_window']} }}
            QMenuBar {{ {self.wnd_config['stylesheets']['menu_bar']} }}
            QLineEdit {{ {self.wnd_config['stylesheets']['line_edit']} }}
        ''')

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        main_menu = menu_bar.addMenu(self.wnd_config['menu']['main'])  
        crew_gendec_action = main_menu.addAction(self.wnd_config['menu']['crew_gendec'])
        crew_gendec_action.triggered.connect(self.show_crew_gendec)
        briefing_action = main_menu.addAction(self.wnd_config['menu']['briefing'])
        briefing_action.triggered.connect(self.show_briefing)
        
        pick_win_action = main_menu.addAction(self.wnd_config['menu']['pick_win'])
        pick_win_action.triggered.connect(self.pick_window)

    def pick_window(self):
        QApplication.setOverrideCursor(Qt.CrossCursor)
        
        success, message = self.button_logic.pick_window(self.wnd_config['target_window_title'], self.wnd_config['child_window_class'])
        
        QApplication.restoreOverrideCursor()
        
        if success:
            QMessageBox.information(self, "Selected Window", message)
        else:
            QMessageBox.warning(self, "Window Selection Failed", message)

    def setup_central_widget(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

    def show_briefing(self):
        self.clear_main_layout()
        self.briefing_ui = BriefingUI(self.wnd_config, self.main_layout)
        self.briefing_ui.create_ui()

    def show_crew_gendec(self):
        self.clear_main_layout()
        self.crew_gendec_ui = CrewGenDecUI(self.wnd_config, self.main_layout)
        self.crew_gendec_ui.create_ui()

    def clear_main_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()