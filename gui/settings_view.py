import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QGroupBox, QFormLayout, QSpinBox, 
                               QMessageBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt

from gui.theme import StegoShieldTheme

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.config_path = os.path.join(os.getcwd(), 'config', 'scoring.json')
        self.weights_spins = {}
        self.thresholds_spins = {}
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title = QLabel("Risk Scoring Configuration")
        title.setStyleSheet(f"color: {StegoShieldTheme.TEXT_HEADING}; font-size: {StegoShieldTheme.FONT_SIZE_TITLE}px; font-weight: 800;")
        main_layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)
        
        # Indicator Weights Group
        self.grp_weights = QGroupBox("Indicator Weights")
        self.grp_weights.setStyleSheet(f"""
            QGroupBox {{
                background-color: #ffffff;
                border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
                border-left: 4px solid {StegoShieldTheme.ACCENT_BLUE};
                border-radius: 12px;
                margin-top: 2ex;
                padding-top: 15px;
                color: {StegoShieldTheme.TEXT_HEADING};
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: {StegoShieldTheme.TEXT_HEADING};
            }}
        """)
        weights_layout = QFormLayout(self.grp_weights)
        weights_layout.setContentsMargins(20, 24, 20, 20)
        weights_layout.setSpacing(12)
        
        indicators = ['format_mismatch', 'trailing_data', 'high_entropy', 'lsb_anomaly', 'suspicious_strings', 'embedded_executable', 'suspicious_structure', 'metadata_anomaly']
        for ind in indicators:
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setStyleSheet(f"""
                QSpinBox {{
                    background-color: #f8fafc;
                    border: 1px solid {StegoShieldTheme.BORDER_STRONG};
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-weight: 600;
                    color: {StegoShieldTheme.TEXT_PRIMARY};
                }}
            """)
            self.weights_spins[ind] = spin
            lbl = QLabel(ind.replace('_', ' ').title())
            lbl.setStyleSheet(f"color: {StegoShieldTheme.TEXT_PRIMARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px; font-weight: 500;")
            weights_layout.addRow(lbl, spin)
            
        container_layout.addWidget(self.grp_weights)

        # Severity Thresholds Group
        self.grp_thresh = QGroupBox("Severity Thresholds")
        self.grp_thresh.setStyleSheet(f"""
            QGroupBox {{
                background-color: #ffffff;
                border: 1px solid {StegoShieldTheme.BORDER_SUBTLE};
                border-left: 4px solid {StegoShieldTheme.ACCENT_PURPLE};
                border-radius: 12px;
                margin-top: 2ex;
                padding-top: 15px;
                color: {StegoShieldTheme.TEXT_HEADING};
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: {StegoShieldTheme.TEXT_HEADING};
            }}
        """)
        thresh_layout = QFormLayout(self.grp_thresh)
        thresh_layout.setContentsMargins(20, 24, 20, 20)
        thresh_layout.setSpacing(12)
        
        thresholds = ['guarded', 'review', 'high', 'critical']
        for th in thresholds:
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setStyleSheet(f"""
                QSpinBox {{
                    background-color: #f8fafc;
                    border: 1px solid {StegoShieldTheme.BORDER_STRONG};
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-weight: 600;
                    color: {StegoShieldTheme.TEXT_PRIMARY};
                }}
            """)
            self.thresholds_spins[th] = spin
            lbl = QLabel(th.title() + " Threshold")
            lbl.setStyleSheet(f"color: {StegoShieldTheme.TEXT_PRIMARY}; font-size: {StegoShieldTheme.FONT_SIZE_NORMAL}px; font-weight: 500;")
            thresh_layout.addRow(lbl, spin)
            
        container_layout.addWidget(self.grp_thresh)
        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self._save_settings)
        
        self.btn_reset = QPushButton("Reset to Defaults")
        self.btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: #ffffff;
                color: {StegoShieldTheme.TEXT_PRIMARY};
                border: 1px solid {StegoShieldTheme.BORDER_STRONG};
                border-radius: 8px;
                padding: 9px 18px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #f8fafc;
            }}
        """)
        self.btn_reset.clicked.connect(self._reset_defaults)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def _load_settings(self):
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            weights = data.get('weights', {})
            for ind, spin in self.weights_spins.items():
                if ind in weights:
                    spin.setValue(weights[ind])
                    
            thresh = data.get('severity_thresholds', {})
            for th, spin in self.thresholds_spins.items():
                if th in thresh:
                    spin.setValue(thresh[th])
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def _save_settings(self):
        data = {
            "weights": {k: s.value() for k, s in self.weights_spins.items()},
            "severity_thresholds": {k: s.value() for k, s in self.thresholds_spins.items()},
            "max_score": 100
        }
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def _reset_defaults(self):
        defaults = {
            "weights": {
                "format_mismatch": 30,
                "trailing_data": 25,
                "high_entropy": 15,
                "lsb_anomaly": 20,
                "suspicious_strings": 20,
                "embedded_executable": 40,
                "suspicious_structure": 15,
                "metadata_anomaly": 10
            },
            "severity_thresholds": {
                "guarded": 20,
                "review": 40,
                "high": 60,
                "critical": 80
            }
        }
        for ind, spin in self.weights_spins.items():
            spin.setValue(defaults['weights'].get(ind, 20))
        for th, spin in self.thresholds_spins.items():
            spin.setValue(defaults['severity_thresholds'].get(th, 50))
