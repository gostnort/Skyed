from PySide6.QtWidgets import QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from bins.commands_processing.handle_cwd import paste_cwd_to_textbox, process_cwd

class CrewGenDecUI:
    def __init__(self, wnd_config, main_layout):
        self.wnd_config = wnd_config
        self.main_layout = main_layout
        self.capt_input = None
        self.fo_input = None
        self.stw_input = None

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
        button_width = self.wnd_config['crew_gendec_ui']['crew_gendec_button_width']

        # Create buttons
        paste_cwd_button = QPushButton(self.wnd_config['crew_gendec_ui']['paste_cwd'])
        get_gendec_button = QPushButton(self.wnd_config['crew_gendec_ui']['get_gendec'])

        # Apply button styles
        for button in [paste_cwd_button, get_gendec_button]:
            button.setFixedHeight(button.sizeHint().height() * 2)
            button.setFixedWidth(button_width)
            button.setStyleSheet(self.wnd_config['stylesheets']['rounded_button'])

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
        textbox.setStyleSheet("background-color: white;")
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