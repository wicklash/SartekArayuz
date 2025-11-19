"""
Sartek GCS - Ground Control Station
Ana başlatıcı dosya

Bu dosya uygulamayı başlatır.
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.core.serial_worker import SerialWorker

# Konfigürasyon
GCS_PORT = 'COM8'  # GCS dinleme portu
BAUDRATE = 9600    # İletişim hızı


def main():
    """Ana uygulama başlatıcı fonksiyon"""
    # QApplication oluştur
    app = QApplication(sys.argv)
    
    # Ana pencereyi oluştur
    window = MainWindow(GCS_PORT, BAUDRATE, SerialWorker)
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
