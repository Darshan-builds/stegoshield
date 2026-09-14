import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
                               QHeaderView, QFrame)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QDragEnterEvent, QDropEvent

from gui.theme import StegoShieldTheme
from gui.analyze_view import AnalysisWorker

class FileDropArea(QFrame):
    file_dropped = Signal(str)

    def __init__(self, title):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 2px dashed {StegoShieldTheme.BORDER_STRONG};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(8)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-weight: 800; font-size: {StegoShieldTheme.FONT_SIZE_LARGE}px; border: none;")
        
        self.lbl_file = QLabel("Drag & Drop or Click to Select")
        self.lbl_file.setAlignment(Qt.AlignCenter)
        self.lbl_file.setWordWrap(True)
        self.lbl_file.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px; border: none;")
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_file)
        self.file_path = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            self.set_file(urls[0].toLocalFile())

    def mousePressEvent(self, event):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            self.set_file(path)

    def set_file(self, path):
        self.file_path = path
        self.lbl_file.setText(os.path.basename(path))
        self.lbl_file.setStyleSheet(f"color: {StegoShieldTheme.ACCENT_BLUE}; font-weight: 700; border: none;")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 2px solid {StegoShieldTheme.ACCENT_BLUE};
                border-radius: 12px;
            }}
        """)
        self.file_dropped.emit(path)

class CompareView(QWidget):
    def __init__(self):
        super().__init__()
        self._result1 = None
        self._result2 = None
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title = QLabel("Two-File Comparison Analysis")
        title.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; font-weight: 800;")
        main_layout.addWidget(title)

        drop_layout = QHBoxLayout()
        drop_layout.setSpacing(20)
        self.drop1 = FileDropArea("File 1 (Baseline / Clean)")
        self.drop2 = FileDropArea("File 2 (Suspect Carrier)")
        drop_layout.addWidget(self.drop1)
        drop_layout.addWidget(self.drop2)
        main_layout.addLayout(drop_layout)

        self.btn_compare = QPushButton("⚖  Compare Files")
        self.btn_compare.setObjectName("PrimaryButton")
        self.btn_compare.setEnabled(False)
        self.btn_compare.clicked.connect(self._run_comparison)
        main_layout.addWidget(self.btn_compare, alignment=Qt.AlignCenter)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Property", "File 1", "File 2"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.table)

        self.drop1.file_dropped.connect(self._check_ready)
        self.drop2.file_dropped.connect(self._check_ready)

    def _check_ready(self):
        if self.drop1.file_path and self.drop2.file_path:
            self.btn_compare.setEnabled(True)

    def _run_comparison(self):
        self.btn_compare.setEnabled(False)
        self.btn_compare.setText("Analyzing...")
        self.table.setRowCount(0)
        
        self.worker1 = AnalysisWorker(self.drop1.file_path)
        self.worker1.finished.connect(lambda res: self._on_result(1, res))
        self.worker1.start()
        
        self.worker2 = AnalysisWorker(self.drop2.file_path)
        self.worker2.finished.connect(lambda res: self._on_result(2, res))
        self.worker2.start()

    def _on_result(self, file_idx, result):
        if file_idx == 1:
            self._result1 = result
        else:
            self._result2 = result
            
        if self._result1 and self._result2:
            self.btn_compare.setText("⚖  Compare Files")
            self.btn_compare.setEnabled(True)
            self._populate_table()
            self._result1 = None
            self._result2 = None

    def _populate_table(self):
        properties = [
            ("Risk Score", lambda r: str(r.get('risk_assessment', {}).get('score', 0))),
            ("Severity", lambda r: r.get('risk_assessment', {}).get('severity', 'UNKNOWN')),
            ("SHA-256", lambda r: r.get('findings', {}).get('hashing', {}).get('sha256', 'N/A')),
            ("Format", lambda r: r.get('findings', {}).get('format_validator', {}).get('extension', 'N/A')),
            ("File Size", lambda r: f"{r.get('findings', {}).get('format_validator', {}).get('file_size', 0):,} bytes"),
            ("Entropy", lambda r: f"{r.get('findings', {}).get('entropy', {}).get('overall_entropy', 0):.4f}"),
            ("Trailing Data", lambda r: str(r.get('findings', {}).get('trailing_data', {}).get('has_trailing_data', False))),
            ("LSB Assessment", lambda r: r.get('findings', {}).get('lsb_analyzer', {}).get('assessment', 'N/A')),
            ("Structure Assessment", lambda r: r.get('findings', {}).get('png_analyzer', {}).get('assessment', r.get('findings', {}).get('jpeg_analyzer', {}).get('assessment', 'N/A')))
        ]

        self.table.setRowCount(len(properties))
        diff_bg = QColor("#fef3c7") # Soft amber highlight for differences

        for row, (prop_name, extractor) in enumerate(properties):
            val1 = extractor(self._result1)
            val2 = extractor(self._result2)

            item_prop = QTableWidgetItem(prop_name)
            item1 = QTableWidgetItem(val1)
            item2 = QTableWidgetItem(val2)
            
            # Highlight differences
            if val1 != val2:
                item1.setBackground(diff_bg)
                item2.setBackground(diff_bg)

            self.table.setItem(row, 0, item_prop)
            self.table.setItem(row, 1, item1)
            self.table.setItem(row, 2, item2)
