"""
StegoShield — Visual Theme

Executive Light Theme inspired by Datify Visual Identity (Onest typeface).
Crisp off-white backgrounds, elevated white cards, deep navy typography,
and vibrant cornflower blue and peach accents.
"""

import os
from typing import Optional
from PySide6.QtGui import QFontDatabase, QFont


def load_custom_fonts():
    """Load the Onest font family if available."""
    font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
    if os.path.isdir(font_dir):
        for fname in os.listdir(font_dir):
            if fname.lower().endswith(('.ttf', '.otf')):
                path = os.path.join(font_dir, fname)
                QFontDatabase.addApplicationFont(path)


class StegoShieldTheme:
    """
    Color palette extracted from the Datify Visual Identity reference (Light Mode):
    
    Background: Clean off-white & pure white cards
    Text: High-contrast deep navy and slate
    Accents: Vibrant cornflower blue, peach, emerald, amber, crimson
    Font: Onest (geometric sans-serif)
    """

    # ── Backgrounds (Crisp Modern Light Theme) ──
    BG_DEEPEST  = '#ffffff'       # Sidebar, window background, headers
    BG_PRIMARY  = '#f4f6fa'       # Main content canvas (soft executive off-white)
    BG_ELEVATED = '#ffffff'       # Elevated white cards, containers
    BG_SURFACE  = '#edf2f9'       # Input fields, table headers, hover states
    BG_GLASS    = '#e2ecfc'       # Subtle light blue tinted accent panels

    # Backward-compatible aliases
    BG_SECONDARY = BG_ELEVATED
    BG_CARD      = BG_ELEVATED
    BG_INPUT     = BG_SURFACE
    SIDEBAR_BG   = BG_DEEPEST
    SIDEBAR_ACTIVE = '#e8f0fe'
    SIDEBAR_HOVER  = '#f1f5f9'

    # ── Brand Colors (from Datify image swatches) ──
    ACCENT_BLUE   = '#2563eb'     # Vibrant Cornflower / Royal Blue — primary accent
    ACCENT_PEACH  = '#f97316'     # Warm Peach / Orange — secondary accent
    ACCENT_CYAN   = '#2563eb'     # Alias for primary accent
    ACCENT_TEAL   = '#0284c7'     # Sky Blue accent
    ACCENT_PURPLE = '#7c3aed'     # Royal Violet / Soft Lavender accent

    # ── Risk Severity Colors (High-Contrast Clean Palette) ──
    ACCENT_GREEN  = '#10b981'     # LOW risk / Clean — Emerald Green
    ACCENT_LIME   = '#84cc16'     # GUARDED — Lime Green
    ACCENT_YELLOW = '#eab308'     # REVIEW — Amber Yellow
    ACCENT_ORANGE = '#f97316'     # HIGH — Warm Orange
    ACCENT_RED    = '#ef4444'     # CRITICAL — Crimson Coral Red

    # ── Typography (High-Contrast Deep Navy / Slate) ──
    TEXT_PRIMARY   = '#1e293b'    # Slate 800 — main body text
    TEXT_SECONDARY = '#64748b'    # Slate 500 — muted labels, metadata
    TEXT_HEADING   = '#0a1128'    # Deep Navy 900 — headings, branding
    TEXT_ACCENT    = '#2563eb'    # Cornflower — highlighted text

    # ── Borders & Dividers ──
    BORDER_SUBTLE = '#e2e8f0'     # Crisp light border
    BORDER_STRONG = '#cbd5e1'     # Stronger input/card divider
    BORDER_GLOW   = '#2563eb33'   # Blue glow (20% opacity)
    BORDER        = '#e2e8f0'     # Alias
    SHADOW        = '#0000000a'   # Very soft subtle drop shadow

    # ── Font Typography ──
    FONT_FAMILY     = 'Onest'
    FONT_FALLBACK   = 'Onest, Segoe UI, Inter, -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    FONT_SIZE_SMALL = 11
    FONT_SIZE_NORMAL = 13
    FONT_SIZE_LARGE  = 15
    FONT_SIZE_TITLE  = 20
    FONT_SIZE_HERO   = 34

    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
            /* ── Global ── */
            QWidget {{
                font-family: {cls.FONT_FALLBACK};
                font-size: {cls.FONT_SIZE_NORMAL}px;
                color: {cls.TEXT_PRIMARY};
            }}

            QMainWindow {{
                background-color: {cls.BG_PRIMARY};
            }}

            QLabel {{
                background: transparent;
            }}

            /* ── Sidebar ── */
            QWidget#Sidebar {{
                background-color: {cls.BG_DEEPEST};
                border-right: 1px solid {cls.BORDER_SUBTLE};
            }}

            /* ── Content Area ── */
            QWidget#MainContent {{
                background-color: {cls.BG_PRIMARY};
            }}

            /* ── Buttons ── */
            QPushButton {{
                background-color: {cls.BG_ELEVATED};
                border: 1px solid {cls.BORDER_STRONG};
                border-radius: 8px;
                color: {cls.TEXT_PRIMARY};
                padding: 9px 18px;
                font-family: {cls.FONT_FALLBACK};
                font-size: {cls.FONT_SIZE_NORMAL}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {cls.BG_SURFACE};
                border: 1px solid {cls.ACCENT_BLUE};
                color: {cls.ACCENT_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {cls.BORDER_SUBTLE};
                color: {cls.TEXT_HEADING};
            }}
            QPushButton:disabled {{
                background-color: #f1f5f9;
                color: #94a3b8;
                border: 1px solid #e2e8f0;
            }}

            /* Primary button — Cornflower Blue */
            QPushButton#PrimaryButton {{
                background-color: {cls.ACCENT_BLUE};
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: #1d4ed8;
            }}
            QPushButton#PrimaryButton:pressed {{
                background-color: #1e40af;
            }}
            QPushButton#PrimaryButton:disabled {{
                background-color: #93c5fd;
                color: #ffffff;
            }}

            /* Danger button — Crimson */
            QPushButton#DangerButton {{
                background-color: {cls.ACCENT_RED};
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 8px;
            }}
            QPushButton#DangerButton:hover {{
                background-color: #dc2626;
            }}

            /* Warm button — Peach / Orange */
            QPushButton#WarmButton {{
                background-color: {cls.ACCENT_PEACH};
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 8px;
            }}
            QPushButton#WarmButton:hover {{
                background-color: #ea580c;
            }}

            /* Teal / Sky Blue button */
            QPushButton#TealButton {{
                background-color: {cls.ACCENT_TEAL};
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 8px;
            }}
            QPushButton#TealButton:hover {{
                background-color: #0369a1;
            }}

            /* Purple / Lavender button */
            QPushButton#PurpleButton {{
                background-color: {cls.ACCENT_PURPLE};
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 8px;
            }}
            QPushButton#PurpleButton:hover {{
                background-color: #6d28d9;
            }}

            /* ── Cards & Containers ── */
            QGroupBox, QFrame#Card {{
                background-color: {cls.BG_ELEVATED};
                border: 1px solid {cls.BORDER_SUBTLE};
                border-radius: 12px;
            }}
            QFrame#WarningCard {{
                background-color: #fff1f2;
                border: 1px solid #fecdd3;
                border-radius: 12px;
            }}
            QGroupBox::title {{
                color: {cls.TEXT_HEADING};
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                font-weight: bold;
                font-size: {cls.FONT_SIZE_NORMAL}px;
            }}

            /* ── Inputs ── */
            QLineEdit, QTextEdit, QSpinBox, QComboBox {{
                background-color: #ffffff;
                border: 1px solid {cls.BORDER_STRONG};
                border-radius: 8px;
                color: {cls.TEXT_PRIMARY};
                padding: 8px 12px;
                selection-background-color: {cls.ACCENT_BLUE};
                selection-color: #ffffff;
            }}
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 2px solid {cls.ACCENT_BLUE};
                background-color: #ffffff;
            }}

            /* ── Scrollbars ── */
            QScrollBar:vertical {{
                border: none;
                background-color: {cls.BG_PRIMARY};
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {cls.BORDER_STRONG};
                min-height: 24px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.TEXT_SECONDARY};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {cls.BG_PRIMARY};
                height: 8px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {cls.BORDER_STRONG};
                min-width: 24px;
                border-radius: 4px;
            }}

            /* ── Tables ── */
            QTableWidget {{
                background-color: {cls.BG_ELEVATED};
                alternate-background-color: #fafbfd;
                color: {cls.TEXT_PRIMARY};
                gridline-color: {cls.BORDER_SUBTLE};
                border: 1px solid {cls.BORDER_SUBTLE};
                border-radius: 10px;
                selection-background-color: #e8f0fe;
                selection-color: {cls.TEXT_HEADING};
            }}
            QHeaderView::section {{
                background-color: {cls.BG_SURFACE};
                color: {cls.TEXT_SECONDARY};
                padding: 10px 14px;
                border: none;
                border-bottom: 1px solid {cls.BORDER_STRONG};
                border-right: 1px solid {cls.BORDER_SUBTLE};
                font-weight: 700;
                font-size: {cls.FONT_SIZE_SMALL}px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }}

            /* ── Progress Bar ── */
            QProgressBar {{
                border: 1px solid {cls.BORDER_SUBTLE};
                border-radius: 6px;
                text-align: center;
                background-color: {cls.BG_SURFACE};
                color: {cls.TEXT_PRIMARY};
                font-size: {cls.FONT_SIZE_SMALL}px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {cls.ACCENT_BLUE};
                border-radius: 5px;
            }}

            /* ── Splitter ── */
            QSplitter::handle {{
                background-color: {cls.BORDER_SUBTLE};
                width: 1px;
            }}

            /* ── Scroll Area ── */
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}

            /* ── Message Box ── */
            QMessageBox {{
                background-color: #ffffff;
            }}
            QMessageBox QLabel {{
                color: {cls.TEXT_PRIMARY};
            }}

            /* ── Tool Tips ── */
            QToolTip {{
                background-color: {cls.TEXT_HEADING};
                color: #ffffff;
                border: 1px solid {cls.TEXT_HEADING};
                border-radius: 6px;
                padding: 6px 10px;
            }}

            /* ── Status Bar ── */
            QStatusBar {{
                background-color: {cls.BG_DEEPEST};
                color: {cls.TEXT_SECONDARY};
                border-top: 1px solid {cls.BORDER_SUBTLE};
                font-size: {cls.FONT_SIZE_SMALL}px;
            }}
        """

    @classmethod
    def severity_color(cls, severity_name: str) -> str:
        """Return the color associated with a severity level."""
        name = severity_name.upper().strip()
        mapping = {
            'LOW': cls.ACCENT_GREEN,
            'SAFE': cls.ACCENT_GREEN,
            'CLEAN': cls.ACCENT_GREEN,
            'SUCCESS': cls.ACCENT_GREEN,
            'GUARDED': cls.ACCENT_LIME,
            'ELEVATED': cls.ACCENT_LIME,
            'REVIEW': cls.ACCENT_YELLOW,
            'MEDIUM': cls.ACCENT_YELLOW,
            'HIGH': cls.ACCENT_ORANGE,
            'CRITICAL': cls.ACCENT_RED,
            'SEVERE': cls.ACCENT_RED,
        }
        return mapping.get(name, cls.TEXT_SECONDARY)

    @classmethod
    def risk_gradient(cls, score) -> str:
        """Return a color hex for a risk score (0-100)."""
        s = float(score)
        if s < 20:
            return cls.ACCENT_GREEN
        elif s < 40:
            return cls.ACCENT_LIME
        elif s < 60:
            return cls.ACCENT_YELLOW
        elif s < 80:
            return cls.ACCENT_ORANGE
        else:
            return cls.ACCENT_RED
