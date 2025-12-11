# dual_connection_control_widget.py
# Alıcı ve Verici port bağlantı kontrolleri

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import pyqtSignal, QTimer


class DualConnectionControlWidget(QWidget):
    """
    Hem alıcı hem de verici port için bağlantı kontrolleri.
    Her port için ayrı bağlan/bağlantıyı kes butonları içerir.
    """
    
    # Sinyaller - Alıcı Port
    receiver_connect_requested = pyqtSignal()
    receiver_disconnect_requested = pyqtSignal()
    
    # Sinyaller - Verici Port
    transmitter_connect_requested = pyqtSignal()
    transmitter_disconnect_requested = pyqtSignal()
    
    def __init__(self, button_styles, parent=None):
        super().__init__(parent)
        self.button_styles = button_styles
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Alıcı Port Kontrolleri
        receiver_frame = self._create_port_control_frame(
            "Alıcı Port Bağlantısı",
            "receiver"
        )
        
        # Verici Port Kontrolleri
        transmitter_frame = self._create_port_control_frame(
            "Verici Port Bağlantısı",
            "transmitter"
        )
        
        main_layout.addWidget(receiver_frame)
        main_layout.addWidget(transmitter_frame)
    
    def _create_port_control_frame(self, title, port_type):
        """
        Port kontrol frame'i oluşturur.
        
        Args:
            title: Frame başlığı
            port_type: 'receiver' veya 'transmitter'
        """
        frame = QFrame()
        frame.setObjectName(f"{port_type}_frame")
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 6px;
                border: 1px solid #3d3d3d;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #e0e0e0;
            font-size: 13px;
            font-weight: bold;
        """)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        connect_button = QPushButton("Bağlan")
        connect_button.setStyleSheet(self.button_styles['connect'])
        
        disconnect_button = QPushButton("Bağlantıyı Kes")
        disconnect_button.setStyleSheet(self.button_styles['disconnect'])
        disconnect_button.setEnabled(False)
        
        # Butonları sakla
        if port_type == "receiver":
            self.receiver_connect_button = connect_button
            self.receiver_disconnect_button = disconnect_button
            connect_button.clicked.connect(self._on_receiver_connect_clicked)
            disconnect_button.clicked.connect(self._on_receiver_disconnect_clicked)
        else:
            self.transmitter_connect_button = connect_button
            self.transmitter_disconnect_button = disconnect_button
            connect_button.clicked.connect(self._on_transmitter_connect_clicked)
            disconnect_button.clicked.connect(self._on_transmitter_disconnect_clicked)
        
        button_layout.addWidget(connect_button)
        button_layout.addWidget(disconnect_button)
        
        layout.addWidget(title_label)
        layout.addLayout(button_layout)
        
        return frame
    
    # Alıcı Port Metodları
    def _on_receiver_connect_clicked(self):
        """Alıcı port bağlan butonuna tıklandığında."""
        self._animate_button(self.receiver_connect_button, "#4caf50", "#81c784")
        self.receiver_connect_requested.emit()
    
    def _on_receiver_disconnect_clicked(self):
        """Alıcı port bağlantıyı kes butonuna tıklandığında."""
        self._animate_button(self.receiver_disconnect_button, "#f44336", "#e57373")
        self.receiver_disconnect_requested.emit()
    
    def set_receiver_connected(self, is_connected):
        """
        Alıcı port bağlantı durumuna göre butonları günceller.
        
        Args:
            is_connected: Bağlantı var mı?
        """
        self.receiver_connect_button.setEnabled(not is_connected)
        self.receiver_disconnect_button.setEnabled(is_connected)
        
        if is_connected:
            self.receiver_disconnect_button.setStyleSheet(self.button_styles['disconnect'])
    
    # Verici Port Metodları
    def _on_transmitter_connect_clicked(self):
        """Verici port bağlan butonuna tıklandığında."""
        self._animate_button(self.transmitter_connect_button, "#4caf50", "#81c784")
        self.transmitter_connect_requested.emit()
    
    def _on_transmitter_disconnect_clicked(self):
        """Verici port bağlantıyı kes butonuna tıklandığında."""
        self._animate_button(self.transmitter_disconnect_button, "#f44336", "#e57373")
        self.transmitter_disconnect_requested.emit()
    
    def set_transmitter_connected(self, is_connected):
        """
        Verici port bağlantı durumuna göre butonları günceller.
        
        Args:
            is_connected: Bağlantı var mı?
        """
        self.transmitter_connect_button.setEnabled(not is_connected)
        self.transmitter_disconnect_button.setEnabled(is_connected)
        
        if is_connected:
            self.transmitter_disconnect_button.setStyleSheet(self.button_styles['disconnect'])
    
    # Yardımcı Metodlar
    def _animate_button(self, button, original_color, flash_color):
        """Buton tıklama animasyonu."""
        button.setStyleSheet(f"QPushButton {{ background-color: {flash_color}; color: white; }}")
        QTimer.singleShot(200, lambda: self._restore_button_style(button))
    
    def _restore_button_style(self, button):
        """Buton stilini geri yükle."""
        if button in [self.receiver_connect_button, self.transmitter_connect_button]:
            button.setStyleSheet(self.button_styles['connect'])
        else:
            button.setStyleSheet(self.button_styles['disconnect'])
