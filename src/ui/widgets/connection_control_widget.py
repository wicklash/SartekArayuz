# connection_control_widget.py
# Bağlantı kontrol widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal


class ConnectionControlWidget(QWidget):
    """
    Seri port bağlantı kontrolleri.
    """
    
    # Sinyaller
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    
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
        self.section_label = QLabel("📡 Bağlantı Kontrolü")
        self.section_label.setObjectName("section_title")
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.connect_button = QPushButton("🔗 Bağlan")
        self.connect_button.setStyleSheet(self.button_styles['connect'])
        
        self.disconnect_button = QPushButton("🔌 Bağlantıyı Kes")
        self.disconnect_button.setStyleSheet(self.button_styles['disconnect'])
        
        # Sinyal bağlantıları
        self.connect_button.clicked.connect(self.connect_requested.emit)
        self.disconnect_button.clicked.connect(self.disconnect_requested.emit)
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        
        layout.addWidget(self.section_label)
        layout.addLayout(button_layout)
        
        # Başlangıç durumu
        self.disconnect_button.setEnabled(False)
    
    def set_connected(self, is_connected):
        """
        Bağlantı durumuna göre butonları günceller.
        
        Args:
            is_connected: Bağlantı var mı?
        """
        self.connect_button.setEnabled(not is_connected)
        self.disconnect_button.setEnabled(is_connected)
