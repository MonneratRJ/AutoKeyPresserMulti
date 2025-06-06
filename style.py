from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from resource_utils import resource_path

def setup_ui(app):
    app.setFixedSize(500, 500)
    main_layout = QVBoxLayout(app.central_widget)

    app.title_label = QLabel("MoneyRat's KeyPresser Deluxe")
    app.title_label.setAlignment(Qt.AlignCenter)
    app.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
    main_layout.addWidget(app.title_label)

    header_row = QHBoxLayout()
    app.window_combo = QComboBox()
    app.window_combo.setEditable(False)
    app.window_combo.currentIndexChanged.connect(app.on_window_select)
    header_row.addWidget(app.window_combo, stretch=2)
    header_row.addStretch(1)
    app.language_button = QPushButton("Language")
    app.language_button.clicked.connect(app.show_language_menu)
    header_row.addWidget(app.language_button, stretch=0)
    main_layout.addLayout(header_row)

    entry_row = QHBoxLayout()
    app.key_label = QLabel("Key:")
    entry_row.addWidget(app.key_label)
    app.key_entry = QLineEdit()
    app.key_entry.setFixedWidth(60)
    entry_row.addWidget(app.key_entry)
    app.interval_label = QLabel("Interval (ms):")
    entry_row.addWidget(app.interval_label)
    app.interval_entry = QLineEdit()
    app.interval_entry.setFixedWidth(80)
    entry_row.addWidget(app.interval_entry)
    app.add_button = QPushButton("Add")
    entry_row.addWidget(app.add_button)
    app.remove_button = QPushButton("Remove")
    entry_row.addWidget(app.remove_button)
    main_layout.addLayout(entry_row)

    app.table = QTableWidget()
    app.table.setColumnCount(3)
    app.table.setHorizontalHeaderLabels(["Active", "Key", "Interval (ms)"])
    app.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    app.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    app.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
    app.table.setAlternatingRowColors(True)
    app.table.setStyleSheet("QTableWidget::item { text-align: center; } QTableWidget::indicator { margin-left: auto; margin-right: auto; }")
    main_layout.addWidget(app.table, stretch=1)

    button_row = QHBoxLayout()
    app.start_button = QPushButton("Start")
    button_row.addWidget(app.start_button)
    app.stop_button = QPushButton("Stop")
    app.stop_button.setEnabled(False)
    button_row.addWidget(app.stop_button)
    main_layout.addLayout(button_row)

    app.status_label = QLabel("Status: Stopped")
    app.status_label.setStyleSheet("color: red;")
    main_layout.addWidget(app.status_label)
    app.hotkey_label = QLabel("Hotkeys: F7 = Start | F8 = Stop")
    app.hotkey_label.setStyleSheet("color: gray;")
    main_layout.addWidget(app.hotkey_label)
    app.edit_info_label = QLabel("Double-click Active column to toggle, Interval column to edit")
    app.edit_info_label.setStyleSheet("color: gray; font-size: 10px;")
    main_layout.addWidget(app.edit_info_label)

    def open_paypal():
        import webbrowser
        webbrowser.open_new("https://www.paypal.com/donate/?business=RFHNR4TM6KPQ4&no_recurring=0&item_name=A+brazilian+software+developer+and+maker+that+enjoys+giving+back+to+the+community.+Help+me+back+if+you+can.+Much+appreciated%21&currency_code=BRL")
    try:
        pixmap = QPixmap(resource_path("paypaldonatebutton.png"))
        if not pixmap.isNull():
            scaled = pixmap.scaledToWidth(140, Qt.SmoothTransformation)
            app.paypal_button = QPushButton()
            app.paypal_button.setIcon(scaled)
            app.paypal_button.setIconSize(scaled.size())
            app.paypal_button.clicked.connect(open_paypal)
            main_layout.addWidget(app.paypal_button, alignment=Qt.AlignCenter)
        else:
            raise Exception()
    except Exception:
        app.paypal_button = QPushButton("Donate with PayPal")
        app.paypal_button.clicked.connect(open_paypal)
        main_layout.addWidget(app.paypal_button, alignment=Qt.AlignCenter)

    app.add_button.clicked.connect(app.add_key_config)
    app.remove_button.clicked.connect(app.remove_key_config)
    app.start_button.clicked.connect(app.start_pressing)
    app.stop_button.clicked.connect(app.stop_pressing)
    app.language_button.clicked.connect(app.show_language_menu)
    app.table.itemDoubleClicked.connect(app.on_double_click)
    app.key_entry.setText("z")
    app.interval_entry.setText("1000")
    app.checkbuttons = {}
    app.checkbox_vars = {}

    def update_table():
        app.table.setRowCount(0)
        for idx, config in enumerate(app.key_configs):
            app.table.insertRow(idx)
            checkbox = QCheckBox()
            checkbox.setChecked(config['active'])
            checkbox.setStyleSheet("margin-left:auto; margin-right:auto;")
            def on_state_changed(state, row=idx):
                app.key_configs[row]['active'] = (state == Qt.Checked)
                if hasattr(app, 'save_config'):
                    app.save_config()
            checkbox.stateChanged.connect(on_state_changed)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            app.table.setCellWidget(idx, 0, widget)
            key_item = QTableWidgetItem(config['key'])
            key_item.setTextAlignment(Qt.AlignCenter)
            app.table.setItem(idx, 1, key_item)
            interval_item = QTableWidgetItem(str(config['interval']))
            interval_item.setTextAlignment(Qt.AlignCenter)
            app.table.setItem(idx, 2, interval_item)
    app.update_table = update_table

    app.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
    app.table.setStyleSheet("""
        QTableWidget::item { text-align: center; }
        QHeaderView::section { text-align: center; }
        QTableWidget::indicator { margin-left: auto; margin-right: auto; }
    """)
