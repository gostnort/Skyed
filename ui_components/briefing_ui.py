import yaml
import os
import datetime
import re

from PySide6.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from bins import ButtonLogic  # Updated import

class BriefingUI:
    def __init__(self, main_window_config, main_layout):
        self.main_window_config = main_window_config
        self.main_layout = main_layout
        self.arrival_processed = False
        self.load_config()


    def load_config(self):
        resource_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        with open(os.path.join(resource_path, "briefing_ui.yml"), "r") as file:
            self.config = yaml.safe_load(file)


    def create_ui(self):
        label = QLabel(self.config['label'])
        label.setAlignment(Qt.AlignBottom)
        self.main_layout.addWidget(label)
        self.info_box = QLineEdit()
        self.info_box.setText(self.config['info_box_default'])
        self.info_box.setStyleSheet(self.config['stylesheets']['info_box'])
        self.main_layout.addWidget(self.info_box)
        button_layout = QHBoxLayout()
        self.buttons = {
            'arrival': QPushButton(self.config['buttons']['arrival']),
            'departure': QPushButton(self.config['buttons']['departure']),
            'check_names': QPushButton(self.config['buttons']['check_names']),
            'check_seats': QPushButton(self.config['buttons']['check_seats']),
            'export': QPushButton(self.config['buttons']['export'])
        }
        button_height = self.buttons['arrival'].sizeHint().height() * 2
        self.active_style = self.config['stylesheets']['active_button']
        self.inactive_style = self.config['stylesheets']['inactive_button']
        for name, button in self.buttons.items():
            button.setFixedHeight(button_height)
            if name == 'arrival':
                button.setStyleSheet(self.active_style)
            else:
                button.setStyleSheet(self.inactive_style)
                button.setEnabled(False)
            button.clicked.connect(lambda checked, b=button: self.handle_button_click(b))
            button_layout.addWidget(button)
        self.main_layout.addLayout(button_layout)
        self.text_area = QTextEdit()
        self.main_layout.addWidget(self.text_area)


    def handle_button_click(self, button):
        self.animate_button_click(button)
        if button == self.buttons['arrival']:
            self.process_arrival_input()
        else:
            # Handle other button clicks if necessary
            pass


    def process_arrival_input(self):
        input_text = self.info_box.text().strip()
        try:
            parsed_data = self.parse_input(input_text) 
            self.set_buttons_enabled(False)
            # Create a ButtonLogic instance
            button_logic = ButtonLogic()
            # Update the call to arrival_button_logic with the resources_path
            success, message = button_logic.arrival_button_logic('resources', parsed_data)
            # Display all messages in the text_area
            self.text_area.append(f"Processing arrival for: {input_text}")
            self.text_area.append(message)  # This will show all messages from arrival_button_logic
            if success:
                self.text_area.append("Arrival processing completed successfully.")
                self.arrival_processed = True
                self.set_buttons_enabled(True)
            else:
                self.text_area.append(f"Error: {message}")
                self.set_buttons_enabled(False)
                self.buttons['arrival'].setEnabled(True)
        except Exception as e:
            self.text_area.append(f"Unexpected error: {str(e)}")
            self.set_buttons_enabled(False)
            self.buttons['arrival'].setEnabled(True)


    def parse_input(self, input_text):
        complete_pattern = r'^([A-Z]{2})(\d{3,4})/(\d{3,4})/(\d{2}[A-Z]{3}\d{2})/(\d{2}[A-Z]{3}\d{2})/([A-Z]{3})$'
        shortcut_pattern = r'^(\d{3,4})/([A-Z]{3})$'

        if re.match(complete_pattern, input_text):
            airline, arr_num, dep_num, arr_date, dep_date, arrival = re.match(complete_pattern, input_text).groups()
            return [
                airline,
                f"{airline}{arr_num}",
                f"{airline}{dep_num}",
                arr_date,
                dep_date,
                arrival
            ]
        elif re.match(shortcut_pattern, input_text):
            dep_num, arrival = re.match(shortcut_pattern, input_text).groups()
            today = datetime.date.today()
            return [
                "CA",
                f"CA{int(dep_num) - 1:03d}",
                f"CA{dep_num}",
                today.strftime("%d%b%y").upper(),
                today.strftime("%d%b%y").upper(),
                arrival
            ]
        else:
            raise ValueError("Invalid input format")


    def set_buttons_enabled(self, enabled):
        for name, button in self.buttons.items():
            if name == 'arrival' or (enabled and self.arrival_processed):
                button.setEnabled(enabled)
                button.setStyleSheet(self.active_style)
            elif not enabled:
                button.setEnabled(False)
                button.setStyleSheet(self.inactive_style)


    def animate_button_click(self, button):
        animation = QPropertyAnimation(button, b"pos")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        start = button.pos()
        end = start + QPoint(0, 5)

        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.start()

        reverse_animation = QPropertyAnimation(button, b"pos")
        reverse_animation.setDuration(100)
        reverse_animation.setEasingCurve(QEasingCurve.InOutQuad)
        reverse_animation.setStartValue(end)
        reverse_animation.setEndValue(start)

        animation.finished.connect(reverse_animation.start)