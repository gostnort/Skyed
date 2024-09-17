from PySide6.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from bins.button_logic import Buttons
import datetime
import re

class BriefingUI:
    def __init__(self, wnd_config, main_layout):
        self.wnd_config = wnd_config
        self.main_layout = main_layout
        self.arrival_processed = False
        self.buttons_logic = Buttons('resources')  # Initialize Buttons class
        self.create_ui()

    def create_ui(self):
        # First line: Label
        label = QLabel(self.wnd_config['briefing_ui']['label'])
        label.setAlignment(Qt.AlignBottom)
        self.main_layout.addWidget(label)

        # Second line: Single-line text box
        self.info_box = QLineEdit()
        self.info_box.setText(self.wnd_config['briefing_ui']['info_box_default'])
        self.info_box.setStyleSheet(self.wnd_config['stylesheets']['info_box'])
        self.main_layout.addWidget(self.info_box)

        # Third line: Five buttons
        button_layout = QHBoxLayout()
        self.buttons = {
            'arrival': QPushButton(self.wnd_config['briefing_ui']['buttons']['arrival']),
            'departure': QPushButton(self.wnd_config['briefing_ui']['buttons']['departure']),
            'check_names': QPushButton(self.wnd_config['briefing_ui']['buttons']['check_names']),
            'check_seats': QPushButton(self.wnd_config['briefing_ui']['buttons']['check_seats']),
            'export': QPushButton(self.wnd_config['briefing_ui']['buttons']['export'])
        }

        button_height = self.buttons['arrival'].sizeHint().height() * 2
        rounded_style = self.wnd_config['stylesheets']['rounded_button']
        for name, button in self.buttons.items():
            button.setFixedHeight(button_height)
            button.setStyleSheet(rounded_style)
            button.clicked.connect(lambda checked, b=button: self.handle_button_click(b))
            button_layout.addWidget(button)
            if name != 'arrival':
                button.setEnabled(False)

        self.main_layout.addLayout(button_layout)

        # Fourth line: Multi-line text box with vertical scroll bar
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
        input_sample = self.wnd_config['briefing_ui']['input_sample']

        try:
            parsed_data = self.parse_input(input_text)
            
            # Disable all buttons during processing
            self.set_buttons_enabled(False)

            # Initialize Buttons class with parsed data
            init_success, init_error = self.buttons_logic.initialize(parsed_data)
            if not init_success:
                raise ValueError(f"Failed to initialize Buttons: {init_error}")

            # Call arrival button logic
            success, result = self.buttons_logic.arrival_button_logic()
            if success:
                self.text_area.append("Arrival processing completed successfully.")
                self.text_area.append(result)
                self.arrival_processed = True
                # Enable all buttons after successful processing
                self.set_buttons_enabled(True)
            else:
                self.text_area.append(f"Error: {result}")
                # Re-enable only the arrival button if there was an error
                self.buttons['arrival'].setEnabled(True)

        except ValueError as e:
            self.text_area.append(f"Input Error: {str(e)}. Example: {input_sample}")
            # Re-enable only the arrival button if there was an input error
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
                self.format_date(arr_date),
                self.format_date(dep_date),
                arrival
            ]
        elif re.match(shortcut_pattern, input_text):
            dep_num, arrival = re.match(shortcut_pattern, input_text).groups()
            today = datetime.date.today()
            return [
                "CA",
                f"CA{int(dep_num) - 1:03d}",
                f"CA{dep_num}",
                today.strftime("%d%b%Y").upper(),
                today.strftime("%d%b%Y").upper(),
                arrival
            ]
        else:
            raise ValueError("Invalid input format")

    def format_date(self, date_str):
        return f"{date_str[:5]}20{date_str[5:]}"

    def set_buttons_enabled(self, enabled):
        for name, button in self.buttons.items():
            if name == 'arrival' or (enabled and self.arrival_processed):
                button.setEnabled(enabled)
            elif not enabled:
                button.setEnabled(False)

    def animate_button_click(self, button):
        animation = QPropertyAnimation(button, b"pos")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        start = button.pos()
        end = start + Qt.QPoint(0, 5)

        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.start()

        # Reverse animation
        reverse_animation = QPropertyAnimation(button, b"pos")
        reverse_animation.setDuration(100)
        reverse_animation.setEasingCurve(QEasingCurve.InOutQuad)
        reverse_animation.setStartValue(end)
        reverse_animation.setEndValue(start)

        animation.finished.connect(reverse_animation.start)

    def cleanup(self):
        self.buttons_logic.cleanup()