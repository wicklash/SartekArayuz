# data_log_widget.py
# Ham veri log widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from ..data_log_window import DataLogWindow


class DataLogWidget(QWidget):
    """
    Gelen ham telemetri verilerini gösteren log widget'ı.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(150)  # Maksimum yükseklik
        self.detail_window = None  # Detay penceresi
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
            data: Eklenecek ham veri string'i
        """
        self.log_text.append(data)
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
        if self.detail_window is None:
            self.detail_window = DataLogWindow(self)
        self.detail_window.show()
        self.detail_window.raise_()
        self.detail_window.activateWindow()
