import os
import json
import glob
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                               QTextEdit, QSplitter)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QColor

from gui.theme import StegoShieldTheme

class ReportView(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_reports()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(16)

        # Toolbar
        toolbar = QHBoxLayout()
        title = QLabel("Analysis Reports History")
        title.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; font-weight: 800;")
        
        self.btn_refresh = QPushButton("🔄  Refresh")
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: #ffffff;
                color: {StegoShieldTheme.TEXT_PRIMARY};
                border: 1px solid {StegoShieldTheme.BORDER_STRONG};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #f8fafc;
            }}
        """)
        self.btn_refresh.clicked.connect(self._load_reports)

        self.btn_open_folder = QPushButton("📂  Open Reports Folder")
        self.btn_open_folder.setObjectName("PrimaryButton")
        self.btn_open_folder.clicked.connect(self._open_reports_folder)

        toolbar.addWidget(title)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_open_folder)
        main_layout.addLayout(toolbar)

        # Splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {StegoShieldTheme.BORDER_SUBTLE}; height: 2px; }}")
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Date & Time", "Analyzed Image", "Risk Score", "Severity Classification"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_report_selected)
        splitter.addWidget(self.table)

        # Text Area (JSON preview)
        self.text_detail = QTextEdit()
        self.text_detail.setReadOnly(True)
        self.text_detail.setStyleSheet(f"""
            QTextEdit {{
                background-color: #ffffff;
                color: {StegoShieldTheme.TEXT_PRIMARY};
                border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
                border-radius: 10px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12px;
                padding: 14px;
                line-height: 140%;
            }}
        """)
        splitter.addWidget(self.text_detail)
        
        main_layout.addWidget(splitter, 1)
        self.reports_data = {}

    def _load_reports(self):
        self.table.setRowCount(0)
        self.reports_data = {}
        reports_dir = os.path.join(os.getcwd(), 'reports')
        if not os.path.exists(reports_dir):
            return
            
        json_files = glob.glob(os.path.join(reports_dir, '*.json'))
        self.table.setRowCount(len(json_files))
        
        for row, path in enumerate(json_files):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                timestamp = data.get('timestamp', 'Unknown')
                file_path = data.get('file_path', 'Unknown')
                filename = os.path.basename(file_path)
                score = str(data.get('risk_assessment', {}).get('score', 0))
                severity = data.get('risk_assessment', {}).get('severity', 'UNKNOWN')
                
                self.reports_data[row] = data
                
                self.table.setItem(row, 0, QTableWidgetItem(timestamp))
                self.table.setItem(row, 1, QTableWidgetItem(filename))
                self.table.setItem(row, 2, QTableWidgetItem(score))
                
                item_sev = QTableWidgetItem(severity)
                color = self._get_severity_color(severity)
                item_sev.setForeground(QColor(color))
                self.table.setItem(row, 3, item_sev)
            except Exception:
                pass

    def _on_report_selected(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.text_detail.clear()
            return
        row = selected_items[0].row()
        data = self.reports_data.get(row)
        if data:
            formatted = json.dumps(data, indent=4)
            self.text_detail.setText(formatted)

    def _open_reports_folder(self):
        reports_dir = os.path.join(os.getcwd(), 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(reports_dir))

    def _get_severity_color(self, severity: str) -> str:
        return StegoShieldTheme.severity_color(severity)
