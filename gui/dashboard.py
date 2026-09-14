import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from gui.theme import StegoShieldTheme

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_stats()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)

        # Top section: Title
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        title = QLabel("STEGOSHIELD")
        title.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_HERO}px; font-weight: 800; letter-spacing: 1px;")
        
        subtitle = QLabel("v1.0.0 — Advanced Defensive Steganography Detection & Malware Carrier Analysis")
        subtitle.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_LARGE}px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)

        # Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.lbl_total_scans = self._create_stat_card("TOTAL SCANS", "0", StegoShieldTheme.ACCENT_BLUE, stats_layout)
        self.lbl_clean = self._create_stat_card("CLEAN FILES", "0", StegoShieldTheme.ACCENT_GREEN, stats_layout)
        self.lbl_suspicious = self._create_stat_card("SUSPICIOUS", "0", StegoShieldTheme.ACCENT_YELLOW, stats_layout)
        self.lbl_critical = self._create_stat_card("CRITICAL", "0", StegoShieldTheme.ACCENT_RED, stats_layout)
        
        layout.addLayout(stats_layout)

        # Quick Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(14)
        
        btn_analyze = QPushButton("🔍  Analyze New File")
        btn_analyze.setObjectName("PrimaryButton")
        
        btn_demo = QPushButton("🧪  Run Demo")
        btn_demo.setObjectName("TealButton")
        
        btn_reports = QPushButton("📋  Open Reports")
        btn_reports.setObjectName("PurpleButton")
        
        actions_layout.addWidget(btn_analyze)
        actions_layout.addWidget(btn_demo)
        actions_layout.addWidget(btn_reports)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Recent History Section
        history_label = QLabel("Recent Analysis History")
        history_label.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; font-weight: 700; margin-top: 10px;")
        layout.addWidget(history_label)

        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Filename", "Algorithm", "Risk Score"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.history_table)

    def _create_stat_card(self, title_text, val_text, color, parent_layout):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: {StegoShieldTheme.BG_ELEVATED};
                border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
                border-top: 4px solid {color};
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(8)
        
        val_lbl = QLabel(val_text)
        val_lbl.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 800;")
        
        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px; font-weight: 700; letter-spacing: 0.5px;")
        
        layout.addWidget(val_lbl, alignment=Qt.AlignLeft)
        layout.addWidget(title_lbl, alignment=Qt.AlignLeft)
        
        parent_layout.addWidget(card)
        return val_lbl

    def load_stats(self):
        history_path = os.path.join(os.getcwd(), 'reports', 'history.json')
        if not os.path.exists(history_path):
            self._set_empty_state()
            return
            
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            records = data.get('records', [])
            self.lbl_total_scans.setText(str(len(records)))
            
            clean = sum(1 for r in records if r.get('risk_score', 0) < 0.3)
            suspicious = sum(1 for r in records if 0.3 <= r.get('risk_score', 0) < 0.7)
            critical = sum(1 for r in records if r.get('risk_score', 0) >= 0.7)
            
            self.lbl_clean.setText(str(clean))
            self.lbl_suspicious.setText(str(suspicious))
            self.lbl_critical.setText(str(critical))
            
            self._populate_table(records)
            
        except Exception as e:
            print(f"Error loading stats: {e}")
            self._set_empty_state()

    def _set_empty_state(self):
        self.lbl_total_scans.setText("0")
        self.lbl_clean.setText("0")
        self.lbl_suspicious.setText("0")
        self.lbl_critical.setText("0")

    def _populate_table(self, records):
        self.history_table.setRowCount(0)
        recent = sorted(records, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
        
        for r in recent:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            ts = QTableWidgetItem(r.get('timestamp', 'N/A'))
            fname = QTableWidgetItem(r.get('filename', 'Unknown'))
            algo = QTableWidgetItem(r.get('algorithm', 'Unknown'))
            
            score_val = r.get('risk_score', 0.0)
            score_item = QTableWidgetItem(f"{score_val:.2f}")
            score_item.setForeground(QColor(StegoShieldTheme.risk_gradient(score_val)))
            
            self.history_table.setItem(row, 0, ts)
            self.history_table.setItem(row, 1, fname)
            self.history_table.setItem(row, 2, algo)
            self.history_table.setItem(row, 3, score_item)
