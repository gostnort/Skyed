import yaml
import os
from PySide6.QtWidgets import QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QFont
from bins import paste_cwd_to_textbox, process_cwd  # Updated import

class CrewGenDecUI:
    def __init__(self, main_window_config, main_layout):
        self.main_window_config = main_window_config
        self.main_layout = main_layout
        self.capt_input = None
        self.fo_input = None
        self.stw_input = None
        self.load_config()

    def load_config(self):
        resource_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        with open(os.path.join(resource_path, "crew_gendec_ui.yml"), "r") as file:
            self.config = yaml.safe_load(file)

    def create_ui(self):
        CENTER_MARGIN = 10
        # Create two multi-line text boxes
        self.left_text_box = QTextEdit()
        self.right_text_box = QTextEdit()

        # Set font to Courier New for text boxes
        courier_font = QFont("Courier New")
        self.left_text_box.setFont(courier_font)
        self.right_text_box.setFont(courier_font)

        # Get button width from config
        button_width = self.config['crew_gendec_button_width']

        # Create buttons
        paste_cwd_button = QPushButton(self.config['paste_cwd'])
        get_gendec_button = QPushButton(self.config['get_gendec'])

        # Apply button styles
        active_style = self.config['stylesheets']['active_button']
        for button in [paste_cwd_button, get_gendec_button]:
            button.setFixedHeight(button.sizeHint().height() * 2)
            button.setFixedWidth(button_width)
            button.setStyleSheet(active_style)

        # Connect button signals to slots
        paste_cwd_button.clicked.connect(self.on_paste_cwd_clicked)
        get_gendec_button.clicked.connect(self.on_get_gendec_clicked)

        # Create new labeled text boxes
        capt_textbox, self.capt_input = self.create_labeled_textbox("CAPT")
        fo_textbox, self.fo_input = self.create_labeled_textbox("FO")
        stw_textbox, self.stw_input = self.create_labeled_textbox("STW")

        # Create layout for center column
        center_layout = QVBoxLayout()
        center_layout.addWidget(capt_textbox)
        center_layout.addWidget(fo_textbox)
        center_layout.addWidget(stw_textbox)
        center_layout.addWidget(paste_cwd_button)
        center_layout.addWidget(get_gendec_button)
        center_layout.addStretch(1)  # Add stretch to push widgets to the top

        # Create a widget to hold the center layout and set its fixed width
        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        center_widget.setFixedWidth(button_width + CENTER_MARGIN)

        # Create main layout for Crew GenDec UI
        gendec_layout = QHBoxLayout()
        gendec_layout.addWidget(self.left_text_box)
        gendec_layout.addWidget(center_widget)
        gendec_layout.addWidget(self.right_text_box)

        # Add the gendec_layout to the main layout
        self.main_layout.addLayout(gendec_layout)

    def create_labeled_textbox(self, label_text):
        widget = QWidget()
        widget.setFixedHeight(30)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text)
        textbox = QLineEdit()
        textbox.setStyleSheet(self.config['stylesheets']['info_box'])
        layout.addWidget(label)
        layout.addWidget(textbox)
        return widget, textbox

    def on_paste_cwd_clicked(self):
        paste_cwd_to_textbox(self.left_text_box)

    def on_get_gendec_clicked(self):
        cwd_text = self.left_text_box.toPlainText()
        capt_count = int(self.capt_input.text() or 0)
        fo_count = int(self.fo_input.text() or 0)
        stw_count = int(self.stw_input.text() or 0)
        processed_cwd = process_cwd(cwd_text, capt_count, fo_count, stw_count)
        self.right_text_box.setText(processed_cwd)