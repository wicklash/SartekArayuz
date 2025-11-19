"""
Sartek GCS - Ground Control Station
Ana başlatıcı dosya

Bu dosya uygulamayı başlatır.
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

# Konfigürasyon
GCS_PORT = 'COM8'  # GCS dinleme portu
BAUDRATE = 9600    # İletişim hızı


def main():
    """Ana uygulama başlatıcı fonksiyon"""
    # QApplication oluştur
    app = QApplication(sys.argv)
    
    # Ana pencereyi oluştur (worker_class parametresi artık gerekmiyor)
    window = MainWindow(GCS_PORT, BAUDRATE, None)
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
