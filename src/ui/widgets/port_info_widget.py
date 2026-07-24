# port_info_widget.py
# Port bilgi gösterimi ve seçimi widget'ı
# Alıcı Port (GCS) ve Verici Port (Simulator) seçimi

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from ...core.config import get_available_ports


class PortInfoWidget(QWidget):
    """
    Port bilgilerini gösteren ve port seçimi yapan widget.
    Alıcı Port (GCS için) ve Verici Port (Simulator için) seçimi yapar.
    """
    
    # Sinyaller
    receiver_port_selected = pyqtSignal(str)   # Alıcı port seçildiğinde
    transmitter_port_selected = pyqtSignal(str)  # Verici port seçildiğinde
    
    def __init__(self, initial_receiver_port="Port seçilmedi", initial_transmitter_port="Port seçilmedi", parent=None):
        super().__init__(parent)
        self.selected_receiver_port = initial_receiver_port
        self.selected_transmitter_port = initial_transmitter_port
        self._setup_ui()
        self._refresh_ports()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Alıcı Port etiketi ve dropdown
        receiver_label = QLabel("Alıcı Port:")
        receiver_label.setStyleSheet("color: #e0e0e0; font-size: 12px; font-weight: bold;")
        receiver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.receiver_port_combo = QComboBox()
        self.receiver_port_combo.setStyleSheet(self._get_combo_style())
        self.receiver_port_combo.currentTextChanged.connect(self._on_receiver_port_changed)
        
        # Verici Port etiketi ve dropdown
        transmitter_label = QLabel("Verici Port:")
        transmitter_label.setStyleSheet("color: #e0e0e0; font-size: 12px; font-weight: bold;")
        transmitter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.transmitter_port_combo = QComboBox()
        self.transmitter_port_combo.setStyleSheet(self._get_combo_style())
        self.transmitter_port_combo.currentTextChanged.connect(self._on_transmitter_port_changed)
        
        # Yenile butonu
        refresh_button = QPushButton("🔄")
        refresh_button.setToolTip("Port listesini yenile")
        refresh_button.setStyleSheet(self._get_refresh_button_style())
        refresh_button.clicked.connect(self._refresh_ports)
        
        # Checksum / CRC durum etiketi (Arayüzde boş duran sağ alanda gösterilir)
        self.checksum_status_label = QLabel("CRC: Bekleniyor...")
        self.checksum_status_label.setStyleSheet("""
            QLabel {
                color: #a0a0a0;
                font-size: 11px;
                font-weight: bold;
                background-color: #2b2b2b;
                padding: 6px 10px;
                border-radius: 4px;
                border: 1px solid #3d3d3d;
            }
        """)
        
        # Layout'a ekle
        layout.addWidget(receiver_label)
        layout.addWidget(self.receiver_port_combo, 1)  # ComboBox genişleyebilir
        layout.addWidget(transmitter_label)
        layout.addWidget(self.transmitter_port_combo, 1)  # ComboBox genişleyebilir
        layout.addWidget(refresh_button)
        layout.addWidget(self.checksum_status_label)
        layout.addStretch()
    
    def update_checksum_status(self, has_error: bool, calculated: int, received: int):
        """CRC/Checksum durumunu arayüzdeki etikete yansıtır."""
        if has_error:
            self.checksum_status_label.setText(f"⚠️ CRC Uyuşmazlığı (Hesaplanan: {calculated} | Alınan: {received})")
            self.checksum_status_label.setStyleSheet("""
                QLabel {
                    color: #ffaa00;
                    font-size: 11px;
                    font-weight: bold;
                    background-color: #3a2e00;
                    padding: 6px 10px;
                    border-radius: 4px;
                    border: 1px solid #ffaa00;
                }
            """)
        else:
            self.checksum_status_label.setText(f"✅ CRC OK ({received})")
            self.checksum_status_label.setStyleSheet("""
                QLabel {
                    color: #00ff88;
                    font-size: 11px;
                    font-weight: bold;
                    background-color: #002e18;
                    padding: 6px 10px;
                    border-radius: 4px;
                    border: 1px solid #00ff88;
                }
            """)
    
    def _get_combo_style(self):
        """ComboBox için stil döndürür."""
        return """
            QComboBox {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                min-height: 30px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 1px solid #5d5d5d;
                background-color: #404040;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #e0e0e0;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: #3d3d3d;
                color: #e0e0e0;
                selection-background-color: #4d4d4d;
                border: 1px solid #4d4d4d;
                padding: 4px;
            }
        """
    
    def _get_refresh_button_style(self):
        """Yenile butonu için stil döndürür."""
        return """
            QPushButton {
                background-color: #3d3d3d;
                color: #e0e0e0;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                min-width: 35px;
                max-width: 35px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border: 1px solid #5d5d5d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """
    
    def _refresh_ports(self):
        """Port listesini yeniler."""
        # Alıcı port seçimini sakla
        current_receiver = self.receiver_port_combo.currentText()
        # Verici port seçimini sakla
        current_transmitter = self.transmitter_port_combo.currentText()
        
        # Her iki combo'yu temizle
        self.receiver_port_combo.clear()
        self.transmitter_port_combo.clear()
        
        ports = get_available_ports()
        if ports:
            # Her iki combo'ya portları ekle
            self.receiver_port_combo.addItems(ports)
            self.transmitter_port_combo.addItems(ports)
            
            # Önceki seçimleri geri yükle (varsa)
            if current_receiver in ports:
                self.receiver_port_combo.setCurrentText(current_receiver)
            elif ports:
                self.receiver_port_combo.setCurrentIndex(0)
                self._on_receiver_port_changed(ports[0])
            
            if current_transmitter in ports:
                self.transmitter_port_combo.setCurrentText(current_transmitter)
            elif ports:
                self.transmitter_port_combo.setCurrentIndex(0)
                self._on_transmitter_port_changed(ports[0])
        else:
            self.receiver_port_combo.addItem("Port bulunamadı")
            self.transmitter_port_combo.addItem("Port bulunamadı")
            self.selected_receiver_port = "Port seçilmedi"
            self.selected_transmitter_port = "Port seçilmedi"
    
    def _on_receiver_port_changed(self, port):
        """
        Alıcı port değiştiğinde çağrılır.
        
        Args:
            port: Seçilen port adı
        """
        if port and port != "Port bulunamadı":
            self.selected_receiver_port = port
            self.receiver_port_selected.emit(port)
    
    def _on_transmitter_port_changed(self, port):
        """
        Verici port değiştiğinde çağrılır.
        
        Args:
            port: Seçilen port adı
        """
        if port and port != "Port bulunamadı":
            self.selected_transmitter_port = port
            self.transmitter_port_selected.emit(port)
    
    def get_receiver_port(self):
        """
        Seçili alıcı portu döndürür.
        
        Returns:
            str: Seçili alıcı port adı veya None
        """
        port = self.receiver_port_combo.currentText()
        if port and port != "Port bulunamadı":
            return port
        return None
    
    def get_transmitter_port(self):
        """
        Seçili verici portu döndürür.
        
        Returns:
            str: Seçili verici port adı veya None
        """
        port = self.transmitter_port_combo.currentText()
        if port and port != "Port bulunamadı":
            return port
        return None
    
    def set_receiver_port_enabled(self, enabled):
        """
        Alıcı port seçimini etkin/devre dışı bırakır.
        
        Args:
            enabled: True ise etkin, False ise devre dışı
        """
        self.receiver_port_combo.setEnabled(enabled)
    
    def set_transmitter_port_enabled(self, enabled):
        """
        Verici port seçimini etkin/devre dışı bırakır.
        
        Args:
            enabled: True ise etkin, False ise devre dışı
        """
        self.transmitter_port_combo.setEnabled(enabled)
    
    def set_ports_enabled(self, enabled):
        """
        Her iki port seçimini de etkin/devre dışı bırakır.
        
        Args:
            enabled: True ise etkin, False ise devre dışı
        """
        self.set_receiver_port_enabled(enabled)
        self.set_transmitter_port_enabled(enabled)
    
    # Geriye uyumluluk için eski metodlar
    def get_selected_port(self):
        """
        Seçili alıcı portu döndürür (geriye uyumluluk için).
        
        Returns:
            str: Seçili alıcı port adı veya None
        """
        return self.get_receiver_port()
    
    def set_port_enabled(self, enabled):
        """
        Alıcı port seçimini etkin/devre dışı bırakır (geriye uyumluluk için).
        
        Args:
            enabled: True ise etkin, False ise devre dışı
        """
        self.set_receiver_port_enabled(enabled)
    
    def port_selected(self):
        """
        Geriye uyumluluk için - receiver_port_selected sinyalini döndürür.
        """
        return self.receiver_port_selected
