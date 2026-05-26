"""
Sartek GCS - Ground Control Station
Ana başlatıcı dosya

Bu dosya uygulamayı başlatır.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.core.config import get_resource_path


def main():
    """Ana uygulama başlatıcı fonksiyon"""
    # Windows görev çubuğunda ikonu göstermek için AppUserModelID ayarla
    # (QApplication öncesi yapılmalı)
    try:
        from ctypes import windll
        myappid = 'sartek.gcs.roket.telemetri.1.0'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    # QApplication oluştur
    app = QApplication(sys.argv)

    # İkon yolunu çöz (EXE ve geliştirme ortamında çalışır)
    icon_path = get_resource_path('assets/icon.ico')

    # Uygulama ikonunu ayarla (görev çubuğu ve pencere başlığı için)
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)

    # Ana pencereyi oluştur (port artık UI'den seçilecek)
    window = MainWindow()
    window.setWindowIcon(app_icon)  # Pencereye de aynı ikonu ata
    window.show()

    # Uygulamayı çalıştır
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

