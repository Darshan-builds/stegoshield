from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Qt

from gui.theme import StegoShieldTheme

class AboutView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Center container
        container = QWidget()
        container.setFixedWidth(700)
        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(16)
        
        # Title
        title = QLabel("STEGOSHIELD")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {StegoShieldTheme.ACCENT_CYAN}; font-size: {StegoShieldTheme.FONT_SIZE_HERO}px; font-weight: bold; letter-spacing: 4px;")
        
        version = QLabel("Version: 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px;")
        
        subtitle = QLabel("Advanced Defensive Steganography Detection & Analysis")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; margin-top: 10px;")
        
        vbox.addWidget(title)
        vbox.addWidget(version)
        vbox.addWidget(subtitle)
        vbox.addSpacing(10)
        
        # Description
        desc = QLabel(
            "StegoShield is a sophisticated analysis suite designed to detect concealed data payloads "
            "within seemingly benign media files. By employing advanced statistical analysis, structural "
            "verification, and heuristic scanning, it helps analysts identify potential steganographic malware carriers."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {StegoShieldTheme.TEXT_PRIMARY}; font-size: {StegoShieldTheme.FONT_SIZE_LARGE}px; line-height: 150%;")
        vbox.addWidget(desc)
        vbox.addSpacing(10)
        
        # Details section
        details_layout = QHBoxLayout()
        
        built_for = QLabel("<b>Built For:</b><br>University Cybersecurity / Malware Analysis Activity")
        built_for.setAlignment(Qt.AlignCenter)
        built_for.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY};")
        
        tech = QLabel("<b>Technology:</b><br>Python, PySide6, NumPy, SciPy, Pillow")
        tech.setAlignment(Qt.AlignCenter)
        tech.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY};")
        
        details_layout.addWidget(built_for)
        details_layout.addWidget(tech)
        vbox.addLayout(details_layout)
        vbox.addSpacing(20)
        
        # Disclaimer Warning Box
        warning_box = QFrame()
        warning_box.setObjectName("WarningCard")
        warning_layout = QVBoxLayout(warning_box)
        warning_layout.setContentsMargins(20, 20, 20, 20)
        
        warning_title = QLabel("⚠ IMPORTANT DISCLAIMER")
        warning_title.setStyleSheet(f"color: {StegoShieldTheme.ACCENT_RED}; font-weight: bold; font-size: {StegoShieldTheme.FONT_SIZE_LARGE}px;")
        warning_title.setAlignment(Qt.AlignCenter)
        
        warning_text = QLabel(
            "This tool performs static/offline analysis only. It does NOT execute, decode, or run "
            "any embedded content. Findings represent statistical indicators and do NOT constitute proof of malware."
        )
        warning_text.setWordWrap(True)
        warning_text.setAlignment(Qt.AlignCenter)
        warning_text.setStyleSheet(f"color: {StegoShieldTheme.TEXT_PRIMARY};")
        
        warning_layout.addWidget(warning_title)
        warning_layout.addWidget(warning_text)
        
        vbox.addWidget(warning_box)
        
        layout.addWidget(container)
