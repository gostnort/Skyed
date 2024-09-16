from PySide6.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class BriefingUI:
    def __init__(self, wnd_config, main_layout):
        self.wnd_config = wnd_config
        self.main_layout = main_layout

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
        buttons = [
            QPushButton(self.wnd_config['briefing_ui']['buttons']['arrival']),
            QPushButton(self.wnd_config['briefing_ui']['buttons']['departure']),
            QPushButton(self.wnd_config['briefing_ui']['buttons']['check_names']),
            QPushButton(self.wnd_config['briefing_ui']['buttons']['check_seats']),
            QPushButton(self.wnd_config['briefing_ui']['buttons']['export'])
        ]
        
        button_height = buttons[0].sizeHint().height() * 2
        rounded_style = self.wnd_config['stylesheets']['rounded_button']
        for button in buttons:
            button.setFixedHeight(button_height)
            button.setStyleSheet(rounded_style)
            button.clicked.connect(lambda checked, b=button: self.animate_button_click(b))
            button_layout.addWidget(button)
        
        self.main_layout.addLayout(button_layout)

        # Fourth line: Multi-line text box with vertical scroll bar
        self.text_area = QTextEdit()
        self.main_layout.addWidget(self.text_area)

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