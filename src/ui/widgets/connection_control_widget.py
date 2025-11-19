# connection_control_widget.py
# Bağlantı kontrol widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QTimer


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
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.connect_button = QPushButton("Bağlan")
        self.connect_button.setStyleSheet(self.button_styles['connect'])
        
        self.disconnect_button = QPushButton("Bağlantıyı Kes")
        self.disconnect_button.setStyleSheet(self.button_styles['disconnect'])
        
        # Sinyal bağlantıları
        self.connect_button.clicked.connect(self._on_connect_clicked)
        self.disconnect_button.clicked.connect(self._on_disconnect_clicked)
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        
        layout.addLayout(button_layout)
        
        # Başlangıç durumu
        self.disconnect_button.setEnabled(False)
    
    def _on_connect_clicked(self):
        """Bağlan butonuna tıklandığında animasyon ve sinyal."""
        self._animate_button(self.connect_button, "#4caf50", "#81c784")
        self.connect_requested.emit()
    
    def _on_disconnect_clicked(self):
        """Bağlantıyı kes butonuna tıklandığında animasyon ve sinyal."""
        self._animate_button(self.disconnect_button, "#f44336", "#e57373")
        self.disconnect_requested.emit()
    
    def _animate_button(self, button, original_color, flash_color):
        """Buton tıklama animasyonu."""
        # Rengi değiştir
        button.setStyleSheet(f"QPushButton {{ background-color: {flash_color}; color: white; }}")
        
        # 200ms sonra eski renge dön
        QTimer.singleShot(200, lambda: self._restore_button_style(button))
    
    def _restore_button_style(self, button):
        """Buton stilini geri yükle."""
        if button == self.connect_button:
            button.setStyleSheet(self.button_styles['connect'])
        else:
            button.setStyleSheet(self.button_styles['disconnect'])
    
    def set_connected(self, is_connected):
        """
        Bağlantı durumuna göre butonları günceller.
        
        Args:
            is_connected: Bağlantı var mı?
        """
        self.connect_button.setEnabled(not is_connected)
        self.disconnect_button.setEnabled(is_connected)
        
        # Disconnect butonu etkin olduğunda bile kırmızı kalsın
        if is_connected:
            self.disconnect_button.setStyleSheet(self.button_styles['disconnect'])
