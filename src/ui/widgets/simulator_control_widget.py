# simulator_control_widget.py
# Simülatör kontrol widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal


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
        
        # Başlık
        self.section_label = QLabel("🚀 Simulatör Kontrolü")
        self.section_label.setObjectName("section_title")
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("▶ Simülatörü Başlat")
        self.stop_button = QPushButton("⏹ Simülatörü Durdur")
        self.stop_button.setStyleSheet(self.button_styles['stop'])
        
        # Sinyal bağlantıları
        self.start_button.clicked.connect(self.start_requested.emit)
        self.stop_button.clicked.connect(self.stop_requested.emit)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        layout.addWidget(self.section_label)
        layout.addLayout(button_layout)
        
        # Başlangıç durumu
        self.stop_button.setEnabled(False)
    
    def set_simulator_running(self, is_running):
        """
        Simülatör durumuna göre butonları günceller.
        
        Args:
            is_running: Simülatör çalışıyor mu?
        """
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
