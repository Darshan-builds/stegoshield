import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QScrollArea, QFrame, 
                               QProgressBar, QSplitter, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon, QFont, QColor

from gui.theme import StegoShieldTheme

from core.analyzer import analyze_file
from core.report_generator import export_json, export_html, generate_report_filename


class ModernScoreWidget(QFrame):
    """
    Modern Executive Threat Score Card Widget.
    Features a clean minimalist card, giant hero score, progress bar gauge, 
    soft-tinted severity pill badge, and contextual recommendation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModernScoreCard")
        self._setup_ui()
        self.reset()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame#ModernScoreCard {{
                background-color: #ffffff;
                border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # Header Row: Title & Status Indicator Dot
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("THREAT RISK SCORE")
        self.lbl_title.setStyleSheet(f"""
            color: {StegoShieldTheme.TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.2px;
        """)
        
        self.lbl_dot = QLabel("●")
        self.lbl_dot.setStyleSheet(f"color: {StegoShieldTheme.BORDER_STRONG}; font-size: 14px;")
        
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_dot)
        layout.addLayout(header_layout)

        # Score Row (Giant Bold Number + subtle /100)
        score_layout = QHBoxLayout()
        score_layout.setSpacing(6)
        score_layout.setAlignment(Qt.AlignLeft)
        
        self.lbl_score = QLabel("0")
        self.lbl_score.setStyleSheet(f"""
            color: {StegoShieldTheme.TEXT_HEADING};
            font-size: 44px;
            font-weight: 800;
            line-height: 100%;
        """)
        
        self.lbl_max = QLabel("/ 100")
        self.lbl_max.setStyleSheet(f"""
            color: {StegoShieldTheme.TEXT_SECONDARY};
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 6px;
        """)
        
        score_layout.addWidget(self.lbl_score)
        score_layout.addWidget(self.lbl_max, alignment=Qt.AlignBottom)
        score_layout.addStretch()
        layout.addLayout(score_layout)

        # Progress Meter Bar
        self.bar = QProgressBar()
        self.bar.setFixedHeight(8)
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #f1f5f9;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #cbd5e1;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.bar)

        # Severity Pill Badge
        badge_layout = QHBoxLayout()
        self.lbl_badge = QLabel("READY")
        self.lbl_badge.setAlignment(Qt.AlignCenter)
        self.lbl_badge.setFixedHeight(28)
        self.lbl_badge.setStyleSheet(f"""
            background-color: #f1f5f9;
            color: {StegoShieldTheme.TEXT_SECONDARY};
            border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
            border-radius: 14px;
            font-size: 12px;
            font-weight: 700;
            padding: 0 14px;
        """)
        badge_layout.addWidget(self.lbl_badge)
        badge_layout.addStretch()
        layout.addLayout(badge_layout)

        # Guidance Recommendation
        self.lbl_desc = QLabel("Select an image to evaluate risk.")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: 12px; line-height: 130%;")
        layout.addWidget(self.lbl_desc)

    def set_score(self, score: int, severity: str, explanation: str = ""):
        sev = severity.upper().strip()
        self.bar.setValue(min(100, max(0, score)))
        self.lbl_score.setText(str(score))
        
        styles = {
            'LOW': {
                'color': '#10b981',
                'bg_badge': '#ecfdf5',
                'border_badge': '#a7f3d0',
                'text_badge': '#047857',
                'desc': 'No significant steganographic anomalies detected.'
            },
            'GUARDED': {
                'color': '#84cc16',
                'bg_badge': '#f7fee7',
                'border_badge': '#d9f99d',
                'text_badge': '#4d7c0f',
                'desc': 'Minor statistical anomalies. Standard inspection recommended.'
            },
            'REVIEW': {
                'color': '#eab308',
                'bg_badge': '#fefce8',
                'border_badge': '#fde047',
                'text_badge': '#a16207',
                'desc': 'Suspicious structural markers present. Further inspection advised.'
            },
            'HIGH': {
                'color': '#f97316',
                'bg_badge': '#fff7ed',
                'border_badge': '#fed7aa',
                'text_badge': '#c2410c',
                'desc': 'Multiple suspicious indicators found. Potential carrier payload.'
            },
            'CRITICAL': {
                'color': '#ef4444',
                'bg_badge': '#fef2f2',
                'border_badge': '#fecaca',
                'text_badge': '#b91c1c',
                'desc': 'Critical payload signatures identified. Quarantine file immediately.'
            }
        }
        
        st = styles.get(sev, {
            'color': '#2563eb',
            'bg_badge': '#eff6ff',
            'border_badge': '#bfdbfe',
            'text_badge': '#1d4ed8',
            'desc': explanation or 'Analysis complete.'
        })
        
        c = st['color']
        self.lbl_score.setStyleSheet(f"color: {c}; font-size: 44px; font-weight: 800;")
        self.lbl_dot.setStyleSheet(f"color: {c}; font-size: 14px;")
        
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #f1f5f9;
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {c};
                border-radius: 4px;
            }}
        """)
        
        self.lbl_badge.setText(f"●  {sev}")
        self.lbl_badge.setStyleSheet(f"""
            background-color: {st['bg_badge']};
            color: {st['text_badge']};
            border: 1px solid {st['border_badge']};
            border-radius: 14px;
            font-size: 12px;
            font-weight: 700;
            padding: 0 14px;
        """)
        
        self.lbl_desc.setText(st.get('desc', 'Analysis evaluation complete.'))

    def reset(self):
        self.bar.setValue(0)
        self.lbl_score.setText("0")
        self.lbl_score.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: 44px; font-weight: 800;")
        self.lbl_dot.setStyleSheet(f"color: {StegoShieldTheme.BORDER_STRONG}; font-size: 14px;")
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #f1f5f9;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #cbd5e1;
                border-radius: 4px;
            }
        """)
        self.lbl_badge.setText("READY")
        self.lbl_badge.setStyleSheet(f"""
            background-color: #f1f5f9;
            color: {StegoShieldTheme.TEXT_SECONDARY};
            border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
            border-radius: 14px;
            font-size: 12px;
            font-weight: 700;
            padding: 0 14px;
        """)
        self.lbl_desc.setText("Select an image to evaluate risk.")


class AnalysisWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            result = analyze_file(self.file_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class AnalyzeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._last_result = None
        self._current_file = None
        self._setup_ui()
        
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top Bar
        top_bar = QFrame()
        top_bar.setStyleSheet(f"background-color: {StegoShieldTheme.BG_ELEVATED}; border-bottom: 1px solid {StegoShieldTheme.BORDER_SUBTLE};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)
        top_layout.setSpacing(12)
        
        self.btn_select = QPushButton("📂  Select Image")
        self.btn_select.setFixedHeight(36)
        self.btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: {StegoShieldTheme.BG_SURFACE};
                color: {StegoShieldTheme.TEXT_PRIMARY};
                border: 1px solid {StegoShieldTheme.BORDER_STRONG};
                border-radius: 8px;
                padding: 0 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #e2e8f0;
                border-color: {StegoShieldTheme.ACCENT_BLUE};
                color: {StegoShieldTheme.ACCENT_BLUE};
            }}
        """)
        
        self.lbl_filepath = QLabel("No file selected")
        self.lbl_filepath.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px;")
        
        self.btn_analyze = QPushButton("🔍  Analyze Image")
        self.btn_analyze.setObjectName("PrimaryButton")
        self.btn_analyze.setFixedHeight(36)
        self.btn_analyze.setMinimumWidth(145)
        self.btn_analyze.setEnabled(False)
        
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setFixedHeight(36)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {StegoShieldTheme.TEXT_SECONDARY};
                border: 1px solid {StegoShieldTheme.BORDER_STRONG};
                border-radius: 8px;
                padding: 0 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #f1f5f9;
                color: {StegoShieldTheme.TEXT_HEADING};
            }}
        """)
        
        top_layout.addWidget(self.btn_select)
        top_layout.addWidget(self.lbl_filepath, 1)
        top_layout.addWidget(self.btn_clear)
        top_layout.addWidget(self.btn_analyze)
        
        main_layout.addWidget(top_bar)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{ border: none; background: #e2e8f0; height: 3px; }}
            QProgressBar::chunk {{ background-color: {StegoShieldTheme.ACCENT_BLUE}; }}
        """)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Splitter for Main Content
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {StegoShieldTheme.BORDER_SUBTLE}; width: 1px; }}")
        
        # Left Panel (Overview & Risk Score)
        left_scroll = QScrollArea()
        left_scroll.setFixedWidth(380)
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet(f"QScrollArea {{ border: none; background-color: {StegoShieldTheme.BG_ELEVATED}; border-right: 1px solid {StegoShieldTheme.BORDER_SUBTLE}; }}")
        
        left_panel = QWidget()
        left_panel.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(14)
        
        self.lbl_thumbnail = QLabel()
        self.lbl_thumbnail.setFixedSize(240, 240)
        self.lbl_thumbnail.setAlignment(Qt.AlignCenter)
        self.lbl_thumbnail.setStyleSheet(f"border: 2px dashed {StegoShieldTheme.BORDER_STRONG}; background-color: #f8fafc; border-radius: 12px; color: {StegoShieldTheme.TEXT_SECONDARY};")
        self.lbl_thumbnail.setText("Drag & Drop Image Here")
        left_layout.addWidget(self.lbl_thumbnail, alignment=Qt.AlignHCenter)
        
        self.lbl_file_info = QLabel("Filename: -\nSize: -\nFormat: -\nSHA-256: -")
        self.lbl_file_info.setWordWrap(True)
        self.lbl_file_info.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px; line-height: 140%;")
        left_layout.addWidget(self.lbl_file_info)
        
        # Modern Threat Score Card
        self.score_card = ModernScoreWidget()
        left_layout.addWidget(self.score_card)
        
        self.lbl_findings = QLabel("Key Findings:\n- No data")
        self.lbl_findings.setWordWrap(True)
        self.lbl_findings.setStyleSheet(f"color: {StegoShieldTheme.TEXT_PRIMARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px; line-height: 140%;")
        left_layout.addWidget(self.lbl_findings)
        left_layout.addStretch()
        
        left_scroll.setWidget(left_panel)
        
        # Right Panel (Detailed Analysis Findings)
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {StegoShieldTheme.BG_PRIMARY};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(28, 24, 28, 24)
        right_layout.setSpacing(16)
        
        lbl_details_header = QLabel("Analysis Details")
        lbl_details_header.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; font-weight: 700;")
        right_layout.addWidget(lbl_details_header)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.modules_container = QWidget()
        self.modules_container.setStyleSheet("background: transparent;")
        self.modules_layout = QVBoxLayout(self.modules_container)
        self.modules_layout.setContentsMargins(0, 0, 0, 0)
        self.modules_layout.setSpacing(12)
        self.modules_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.modules_container)
        
        right_layout.addWidget(scroll_area)
        
        splitter.addWidget(left_scroll)
        splitter.addWidget(right_panel)
        main_layout.addWidget(splitter, 1)
        
        # Bottom Bar
        bottom_bar = QFrame()
        bottom_bar.setStyleSheet(f"background-color: {StegoShieldTheme.BG_ELEVATED}; border-top: 1px solid {StegoShieldTheme.BORDER_SUBTLE};")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(20, 12, 20, 12)
        bottom_layout.setSpacing(12)
        bottom_layout.addStretch()
        
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_json.setStyleSheet(f"""
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
                border-color: {StegoShieldTheme.ACCENT_BLUE};
            }}
        """)
        
        self.btn_export_html = QPushButton("Export HTML")
        self.btn_export_html.setStyleSheet(f"""
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
                border-color: {StegoShieldTheme.ACCENT_BLUE};
            }}
        """)
        
        bottom_layout.addWidget(self.btn_export_json)
        bottom_layout.addWidget(self.btn_export_html)
        main_layout.addWidget(bottom_bar)
        
        # Connections
        self.btn_select.clicked.connect(self._select_file)
        self.btn_analyze.clicked.connect(self._start_analysis)
        self.btn_clear.clicked.connect(self._clear_view)
        self.btn_export_json.clicked.connect(self._export_json)
        self.btn_export_html.clicked.connect(self._export_html)

    def _get_severity_color(self, severity: str) -> str:
        return StegoShieldTheme.severity_color(severity)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            self._set_file(urls[0].toLocalFile())

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File to Analyze", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            self._set_file(path)

    def _set_file(self, path):
        self._current_file = path
        self.lbl_filepath.setText(path)
        self.btn_analyze.setEnabled(True)
        
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.lbl_thumbnail.setPixmap(pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_thumbnail.setStyleSheet(f"border: 1px solid {StegoShieldTheme.BORDER_SUBTLE}; background-color: #f8fafc; border-radius: 12px;")
        else:
            self.lbl_thumbnail.setText("Preview Not Available")

    def _clear_view(self):
        self._current_file = None
        self._last_result = None
        self.lbl_filepath.setText("No file selected")
        self.btn_analyze.setEnabled(False)
        self.lbl_thumbnail.clear()
        self.lbl_thumbnail.setText("Drag & Drop Image Here")
        self.lbl_thumbnail.setStyleSheet(f"border: 2px dashed {StegoShieldTheme.BORDER_STRONG}; background-color: #f8fafc; border-radius: 12px;")
        self.score_card.reset()
        self.lbl_file_info.setText("Filename: -\nSize: -\nFormat: -\nSHA-256: -")
        self.lbl_findings.setText("Key Findings:\n- No data")
        
        while self.modules_layout.count():
            item = self.modules_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _start_analysis(self):
        if not self._current_file: return
        self.btn_analyze.setEnabled(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        
        self.worker = AnalysisWorker(self._current_file)
        self.worker.finished.connect(self._on_analysis_finished)
        self.worker.error.connect(self._on_analysis_error)
        self.worker.start()

    def _on_analysis_error(self, err_msg):
        self.progress_bar.hide()
        self.btn_analyze.setEnabled(True)
        self.lbl_findings.setText(f"Error during analysis:\n{err_msg}")

    def _on_analysis_finished(self, result):
        self.progress_bar.hide()
        self.btn_analyze.setEnabled(True)
        self._last_result = result
        self._populate_results(result)

    def _populate_results(self, result):
        findings = result.get('findings', {})
        fmt = findings.get('format_validator', {})
        hashing = findings.get('hashing', {})
        
        fname = os.path.basename(self._current_file) if self._current_file else "Unknown"
        fsize = fmt.get('file_size', 0)
        ext = fmt.get('extension', 'unknown')
        sha256 = hashing.get('sha256', 'N/A')[:16] + '...'
        
        self.lbl_file_info.setText(f"Filename: {fname}\nSize: {fsize:,} bytes\nFormat: {ext.upper()}\nSHA-256: {sha256}")
        
        risk = result.get('risk_assessment', {})
        score = risk.get('score', 0)
        severity = risk.get('severity', 'UNKNOWN')
        explanation = risk.get('explanation', '')
        
        # Update Modern Score Card
        self.score_card.set_score(score, severity, explanation)
        
        contributors = risk.get('contributors', [])
        findings_text = "<b>Key Findings:</b>\n"
        for c in contributors[:5]:
            findings_text += f"• {c.get('indicator', 'Unknown')} (+{c.get('points', 0)})\n"
        if not contributors:
            findings_text += "• No significant risks detected."
        self.lbl_findings.setText(findings_text)
        
        while self.modules_layout.count():
            item = self.modules_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        modules_order = [
            ("Format Validation", "format_validator"),
            ("Cryptographic Hashes", "hashing"),
            ("Metadata Analysis", "metadata"),
            ("Entropy Analysis", "entropy"),
            ("Trailing Data Detection", "trailing_data"),
            ("PNG Chunk Analysis", "png_analyzer"),
            ("JPEG Structure Analysis", "jpeg_analyzer"),
            ("LSB Statistical Analysis", "lsb_analyzer"),
            ("Noise & Distribution", "noise_analyzer"),
            ("Suspicious Strings", "strings"),
            ("Embedded Data", "embedded_data"),
        ]
        
        for name, key in modules_order:
            if key in findings:
                self._add_module_card(name, findings[key])

    def _add_module_card(self, title, data):
        card = QFrame()
        card.setObjectName("Card")
        
        risk = data.get('risk_contribution', 0)
        border_color = StegoShieldTheme.ACCENT_GREEN
        icon = "✓"
        if risk > 0 and risk < 30:
            border_color = StegoShieldTheme.ACCENT_YELLOW
            icon = "⚠"
        elif risk >= 30:
            border_color = StegoShieldTheme.ACCENT_RED
            icon = "❌"
            
        card.setStyleSheet(f"""
            QFrame#Card {{
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
                border-left: 4px solid {border_color};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        
        header = QLabel(f"{icon}  <b>{title}</b>")
        header.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_LARGE}px; font-weight: 700;")
        layout.addWidget(header)
        
        details = self._format_module_details(data)
        lbl_details = QLabel(details)
        lbl_details.setWordWrap(True)
        lbl_details.setStyleSheet(f"color: {StegoShieldTheme.TEXT_PRIMARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px; line-height: 140%;")
        layout.addWidget(lbl_details)
        
        self.modules_layout.addWidget(card)

    def _format_module_details(self, data):
        lines = []
        for k, v in data.items():
            if k in ('risk_contribution', 'assessment'):
                continue
            if isinstance(v, (list, dict)) and not v:
                continue
            if isinstance(v, list):
                v_str = ", ".join(str(x) for x in v[:5])
                if len(v) > 5: v_str += f" (+{len(v)-5} more)"
            elif isinstance(v, dict):
                v_str = ", ".join(f"{dk}: {dv}" for dk, dv in list(v.items())[:3])
            else:
                v_str = str(v)
            clean_k = k.replace('_', ' ').title()
            lines.append(f"<b>{clean_k}:</b> {v_str}")
            
        assessment = data.get('assessment', '')
        if assessment:
            lines.insert(0, f"<b>Assessment:</b> {assessment}")
            
        return "<br>".join(lines) if lines else "No notable findings."

    def _export_json(self):
        if not self._last_result: return
        path, _ = QFileDialog.getSaveFileName(self, "Export JSON", "", "JSON Files (*.json)")
        if path:
            try:
                export_json(self._last_result, path)
            except Exception as e:
                print(f"Export failed: {e}")

    def _export_html(self):
        if not self._last_result: return
        path, _ = QFileDialog.getSaveFileName(self, "Export HTML", "", "HTML Files (*.html)")
        if path:
            try:
                export_html(self._last_result, path)
            except Exception as e:
                print(f"Export failed: {e}")
