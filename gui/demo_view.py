import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from gui.theme import StegoShieldTheme
from demo import generate_samples
from core import analyzer

class GeneratorWorker(QThread):
    finished = Signal(list)
    def run(self):
        try:
            samples = []
            if hasattr(generate_samples, 'generate_all_samples'):
                res = generate_samples.generate_all_samples()
                for name, info in res.items():
                    samples.append({
                        'name': name,
                        'path': info.get('path', ''),
                        'description': info.get('description', ''),
                        'expected': info.get('expected_risk', 'Unknown')
                    })
            elif hasattr(generate_samples, 'generate_samples'):
                samples = generate_samples.generate_samples()
            self.finished.emit(samples if samples else [])
        except Exception as e:
            print("Generation error:", e)
            self.finished.emit([])

class BatchAnalyzerWorker(QThread):
    finished = Signal(dict)
    def __init__(self, samples):
        super().__init__()
        self.samples = samples
    def run(self):
        results = {}
        for sample in self.samples:
            path = sample.get('path', '')
            if os.path.exists(path):
                try:
                    if hasattr(analyzer, 'analyze_file'):
                        results[path] = analyzer.analyze_file(path)
                    elif hasattr(analyzer, 'analyze'):
                        results[path] = analyzer.analyze(path)
                except Exception as e:
                    print("Batch analysis error:", e)
        self.finished.emit(results)

class DemoView(QWidget):
    def __init__(self):
        super().__init__()
        self.samples = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title = QLabel("DEMO LAB — Safe Synthetic Test Cases")
        title.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; font-weight: 800;")
        main_layout.addWidget(title)

        intro = QLabel("This lab generates synthetic image files containing known steganographic patterns to test StegoShield's detection capabilities. Use this environment to observe how anomalies (LSB modification, trailing bytes) affect the risk assessment.")
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px; line-height: 140%;")
        main_layout.addWidget(intro)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.btn_generate = QPushButton("🧪  Generate Samples")
        self.btn_generate.setObjectName("TealButton")
        self.btn_generate.clicked.connect(self._generate_samples)

        self.btn_analyze = QPushButton("🔍  Analyze All Samples")
        self.btn_analyze.setObjectName("PrimaryButton")
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self._analyze_samples)

        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(self.btn_analyze)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # Cards Layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.cards_layout = QHBoxLayout(container)
        self.cards_layout.setContentsMargins(0, 10, 0, 10)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignLeft)
        scroll.setWidget(container)
        
        main_layout.addWidget(scroll, 1)

        edu = QLabel("<b>Educational Note:</b> StegoShield evaluates indicators including trailing data after EOF, structural irregularities in PNG/JPEG headers, and least significant bit (LSB) statistical shifts. Indicators suggest risk, not confirmed malware.")
        edu.setWordWrap(True)
        edu.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px;")
        main_layout.addWidget(edu)

    def _generate_samples(self):
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Generating...")
        self.gen_worker = GeneratorWorker()
        self.gen_worker.finished.connect(self._on_generated)
        self.gen_worker.start()

    def _on_generated(self, samples):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("🧪  Generate Samples")
        self.samples = samples
        if self.samples:
            self.btn_analyze.setEnabled(True)
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            for s in self.samples:
                card = self._create_card(s.get('name', 'Sample'), s.get('description', ''), None, s.get('expected', 'Unknown'))
                self.cards_layout.addWidget(card)

    def _analyze_samples(self):
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("Analyzing...")
        self.ana_worker = BatchAnalyzerWorker(self.samples)
        self.ana_worker.finished.connect(self._on_analyzed)
        self.ana_worker.start()

    def _on_analyzed(self, results):
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("🔍  Analyze All Samples")
        
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for s in self.samples:
            path = s.get('path', '')
            res = results.get(path)
            card = self._create_card(s.get('name', 'Sample'), s.get('description', ''), res, s.get('expected', 'Unknown'))
            self.cards_layout.addWidget(card)

    def _create_card(self, name, description, result, expected=""):
        card = QFrame()
        card.setFixedWidth(320)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-weight: 800; font-size: {StegoShieldTheme.FONT_SIZE_LARGE}px;")
        layout.addWidget(lbl_name)

        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px; line-height: 130%;")
        layout.addWidget(lbl_desc)

        if result:
            score = result.get('risk_assessment', {}).get('score', 0)
            severity = result.get('risk_assessment', {}).get('severity', 'UNKNOWN')
            color = self._get_severity_color(severity)
            
            score_box = QFrame()
            score_box.setStyleSheet(f"background-color: #f8fafc; border-radius: 8px; border: 2px solid {color}; padding: 10px;")
            sb_layout = QVBoxLayout(score_box)
            sb_layout.setContentsMargins(12, 12, 12, 12)
            sb_layout.setSpacing(2)
            
            lbl_score = QLabel(str(score))
            lbl_score.setAlignment(Qt.AlignCenter)
            lbl_score.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 800;")
            
            lbl_sev = QLabel(severity)
            lbl_sev.setAlignment(Qt.AlignCenter)
            lbl_sev.setStyleSheet(f"color: {color}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px; font-weight: 700;")
            
            sb_layout.addWidget(lbl_score)
            sb_layout.addWidget(lbl_sev)
            layout.addWidget(score_box)
            
            contributors = result.get('risk_assessment', {}).get('contributors', [])
            findings = "<b>Indicators:</b><br>"
            for c in contributors[:3]:
                findings += f"• {c.get('indicator', '')} (+{c.get('points', 0)})<br>"
            if not contributors:
                findings += "• Clean baseline"
            lbl_findings = QLabel(findings)
            lbl_findings.setWordWrap(True)
            lbl_findings.setStyleSheet(f"color: {StegoShieldTheme.TEXT_PRIMARY}; font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px;")
            layout.addWidget(lbl_findings)
            
            lbl_exp = QLabel(f"<b>Expected:</b> {expected}")
            lbl_exp.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-size: {StegoShieldTheme.FONT_SIZE_SMALL}px;")
            layout.addWidget(lbl_exp)
            
        else:
            layout.addStretch()
            lbl_pending = QLabel("Ready to analyze")
            lbl_pending.setAlignment(Qt.AlignCenter)
            lbl_pending.setStyleSheet(f"color: {StegoShieldTheme.TEXT_SECONDARY}; font-style: italic; padding: 20px;")
            layout.addWidget(lbl_pending)
            layout.addStretch()

        return card

    def _get_severity_color(self, severity: str) -> str:
        return StegoShieldTheme.severity_color(severity)
