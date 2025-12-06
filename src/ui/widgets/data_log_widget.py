# data_log_widget.py
# Ham veri log widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from ..data_log_window import DataLogWindow
from ...core.data_parser import TelemetryData


class DataLogWidget(QWidget):
    """
    Gelen ham telemetri verilerini gösteren log widget'ı.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(150)  # Maksimum yükseklik
        self.detail_window = DataLogWindow(self)  # Detay penceresi (her zaman oluşturulur)
        self.detail_window.hide()  # Başlangıçta gizli
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # İmleç değiştir
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Başlık
        title_label = QLabel("Gelen Veri Logları (Tıklayarak detaylı görüntüleyin)")
        title_label.setObjectName("section_title")
        
        # Log text alanı
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #00ff00;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.log_text)
    
    def add_log(self, data):
        """
        Log'a yeni veri ekler.
        
        Args:
            data: TelemetryData nesnesi (parse edilmiş veri) veya bytes/string
        """
        if isinstance(data, TelemetryData):
            # Parse edilmiş telemetri verisi - okunabilir format
            log_line = (f"[#{data.sayac}] Takım: {data.takim_id} | "
                       f"İrtifa: {data.get_formatted_irtifa()} | "
                       f"Durum: {data.durum_text} | "
                       f"Roket GPS: {data.get_formatted_gps_irtifa(data.roket_gps_irtifa)} | "
                       f"Checksum: {data.checksum}")
            self.log_text.append(log_line)
        elif isinstance(data, bytes):
            # Binary veriyi hex formatında göster (fallback)
            hex_str = data.hex().upper()
            # Her 2 karakterden sonra boşluk ekle (daha okunabilir)
            formatted_hex = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
            self.log_text.append(f"[Binary] {formatted_hex}")
        else:
            # String veri
            self.log_text.append(str(data))
        
        # Otomatik scroll (en sona git)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Log'u temizler."""
        self.log_text.clear()
    
    def mousePressEvent(self, event):
        """
        Widget'a tıklandığında detay penceresini açar.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_detail_window()
        super().mousePressEvent(event)
    
    def show_detail_window(self):
        """Detaylı log penceresini açar."""
        self.detail_window.show()
        self.detail_window.raise_()
        self.detail_window.activateWindow()
