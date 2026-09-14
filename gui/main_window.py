"""
StegoShield — Main Application Window

Executive cybersecurity dashboard layout with clean sidebar navigation.
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt, QSize
from gui.theme import StegoShieldTheme
from gui.dashboard import DashboardView
from gui.analyze_view import AnalyzeView
from gui.compare_view import CompareView
from gui.demo_view import DemoView
from gui.report_view import ReportView
from gui.settings_view import SettingsView
from gui.about_view import AboutView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StegoShield — Steganographic Malware Carrier Detection")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 900)
        self.setStyleSheet(StegoShieldTheme.get_stylesheet())

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        self.sidebar_layout = QVBoxLayout(sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)

        # Logo area
        logo_area = QWidget()
        logo_area.setStyleSheet("background: transparent;")
        logo_inner = QVBoxLayout(logo_area)
        logo_inner.setContentsMargins(24, 28, 24, 16)
        logo_inner.setSpacing(4)

        shield_icon = QLabel("🛡")
        shield_icon.setStyleSheet("font-size: 28px; background: transparent;")
        title = QLabel("STEGOSHIELD")
        title.setStyleSheet(
            f"color: {StegoShieldTheme.TEXT_HEADING}; "
            f"font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; "
            f"font-weight: 800; letter-spacing: 2px; background: transparent;"
        )
        tagline = QLabel("Steganography Detection")
        tagline.setStyleSheet(
            f"color: {StegoShieldTheme.ACCENT_BLUE}; "
            f"font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px; "
            f"font-weight: 600; background: transparent;"
        )

        logo_inner.addWidget(shield_icon)
        logo_inner.addWidget(title)
        logo_inner.addWidget(tagline)
        self.sidebar_layout.addWidget(logo_area)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {StegoShieldTheme.BORDER_SUBTLE};")
        self.sidebar_layout.addWidget(sep)
        self.sidebar_layout.addSpacing(12)

        # ── Content stack ──
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("MainContent")

        # Navigation items
        self.nav_buttons = {}
        nav_items = [
            ("🏠", "Dashboard",    DashboardView),
            ("🔍", "Analyze",      AnalyzeView),
            ("⚖",  "Compare",      CompareView),
            ("🧪", "Demo Lab",     DemoView),
            ("📋", "Reports",      ReportView),
            ("⚙",  "Settings",     SettingsView),
        ]

        for icon, name, ViewClass in nav_items:
            self._add_nav_button(icon, name, ViewClass())

        self.sidebar_layout.addStretch()

        # About (at bottom, before version)
        self._add_nav_button("ℹ", "About", AboutView())

        # Version label
        ver = QLabel("v1.0.0")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(
            f"color: {StegoShieldTheme.TEXT_SECONDARY}; "
            f"font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px; "
            f"padding: 12px; background: transparent;"
        )
        self.sidebar_layout.addWidget(ver)

        # ── Content wrapper ──
        content_wrapper = QWidget()
        content_wrapper.setObjectName("MainContent")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.stacked_widget)

        # Assemble
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_wrapper, stretch=1)

        # Default to Dashboard
        self.switch_view("Dashboard")

        # Status bar
        self.statusBar().showMessage("● Ready")
        self.statusBar().setStyleSheet(
            f"background-color: {StegoShieldTheme.BG_DEEPEST}; "
            f"color: {StegoShieldTheme.TEXT_SECONDARY}; "
            f"border-top: 1px solid {StegoShieldTheme.BORDER_SUBTLE}; "
            f"font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px; "
            f"padding: 4px 14px;"
        )

    def _add_nav_button(self, icon: str, name: str, view_widget: QWidget):
        """Add a navigation button to the sidebar and its view to the stack."""
        idx = self.stacked_widget.addWidget(view_widget)

        btn = QPushButton(f"  {icon}   {name}")
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(44)
        btn.setStyleSheet(f"""
            QPushButton#NavButton {{
                background-color: transparent;
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding: 0 20px;
                font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px;
                color: #475569;
                border-radius: 0;
                font-weight: 500;
            }}
            QPushButton#NavButton:hover {{
                background-color: #f1f5f9;
                color: {StegoShieldTheme.TEXT_HEADING};
            }}
            QPushButton#NavButton:checked {{
                background-color: #e8f0fe;
                border-left: 3px solid {StegoShieldTheme.ACCENT_BLUE};
                color: {StegoShieldTheme.ACCENT_BLUE};
                font-weight: 700;
            }}
        """)

        btn.clicked.connect(lambda _, n=name: self.switch_view(n))
        self.sidebar_layout.addWidget(btn)
        self.nav_buttons[name] = (btn, idx)

    def switch_view(self, name: str):
        """Switch to a named view and update button states."""
        for btn_name, (btn, idx) in self.nav_buttons.items():
            btn.setChecked(btn_name == name)
        if name in self.nav_buttons:
            _, idx = self.nav_buttons[name]
            self.stacked_widget.setCurrentIndex(idx)

    def navigate_to_analyze(self):
        self.switch_view("Analyze")
