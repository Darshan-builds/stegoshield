import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def setup_logging():
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=str(log_dir / 'stegoshield.log'),
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

def main():
    setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName('StegoShield')
    app.setApplicationVersion('1.0.0')
    
    from gui.theme import load_custom_fonts, StegoShieldTheme
    load_custom_fonts()
    
    from PySide6.QtGui import QFont
    app.setFont(QFont("Onest", 10))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
