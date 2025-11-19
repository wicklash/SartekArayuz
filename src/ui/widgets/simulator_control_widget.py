# simulator_control_widget.py
# Simülatör kontrol widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor


class SimulatorControlWidget(QWidget):
    """
    Simülatör başlatma ve durdurma kontrolleri.
    """
    
    # Sinyaller
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    
    def __init__(self, button_styles, parent=None):
        super().__init__(parent)
        self.button_styles = button_styles
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("Simülatörü Başlat")
        self.start_button.setStyleSheet(self.button_styles['start'])
        self.stop_button = QPushButton("Simülatörü Durdur")
        self.stop_button.setStyleSheet(self.button_styles['stop'])
        
        # Sinyal bağlantıları
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Başlangıç durumu
        self.stop_button.setEnabled(False)
    
    def _on_start_clicked(self):
        """Başlat butonuna tıklandığında animasyon ve sinyal."""
        self._animate_button(self.start_button, "#4caf50", "#81c784")
        self.start_requested.emit()
    
    def _on_stop_clicked(self):
        """Durdur butonuna tıklandığında animasyon ve sinyal."""
        self._animate_button(self.stop_button, "#f44336", "#e57373")
        self.stop_requested.emit()
    
    def _animate_button(self, button, original_color, flash_color):
        """Buton tıklama animasyonu."""
        # Rengi değiştir
        button.setStyleSheet(f"QPushButton {{ background-color: {flash_color}; color: white; }}")
        
        # 200ms sonra eski renge dön
        QTimer.singleShot(200, lambda: self._restore_button_style(button))
    
    def _restore_button_style(self, button):
        """Buton stilini geri yükle."""
        if button == self.start_button:
            button.setStyleSheet(self.button_styles['start'])
        else:
            button.setStyleSheet(self.button_styles['stop'])
    
    def set_simulator_running(self, is_running):
        """
        Simülatör durumuna göre butonları günceller.
        
        Args:
            is_running: Simülatör çalışıyor mu?
        """
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        
        # Stop butonu etkin olduğunda bile kırmızı kalsın
        if is_running:
            self.stop_button.setStyleSheet(self.button_styles['stop'])
