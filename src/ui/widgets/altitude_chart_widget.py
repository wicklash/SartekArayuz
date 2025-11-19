# altitude_chart_widget.py
# Roket irtifa grafiği widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from collections import deque


class AltitudeChartWidget(QWidget):
    """
    Roket irtifa verilerini gösteren gerçek zamanlı grafik.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.altitude_data = deque(maxlen=100)  # Son 100 veri noktası
        self.max_altitude = 0
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık
        self.title_label = QLabel("Gerçek Zamanlı İrtifa Grafiği")
        self.title_label.setObjectName("section_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.title_label)
        
        # Minimum boyut
        self.setMinimumHeight(300)
    
    def add_altitude(self, altitude_str):
        """
        Yeni irtifa verisi ekler.
        
        Args:
            altitude_str: İrtifa string'i (örn: "1234.5 m")
        """
        try:
            # String'den sayısal değeri çıkar
            altitude_value = float(altitude_str.replace(' m', '').replace(',', '.'))
            self.altitude_data.append(altitude_value)
            
            # Maksimum irtifayı güncelle
            if altitude_value > self.max_altitude:
                self.max_altitude = altitude_value
            
            # Grafiği yeniden çiz
            self.update()
        except (ValueError, AttributeError):
            pass
    
    def paintEvent(self, event):
        """Grafik çizim eventi."""
        super().paintEvent(event)
        
        if len(self.altitude_data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Çizim alanı
        margin = 50
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin - 40  # Başlık için alan
        
        # Arka plan grid
        self._draw_grid(painter, margin, margin + 40, width, height)
        
        # Eksenler
        self._draw_axes(painter, margin, margin + 40, width, height)
        
        # Veri çizgisi
        self._draw_data(painter, margin, margin + 40, width, height)
    
    def _draw_grid(self, painter, x, y, width, height):
        """Grid çizgilerini çizer."""
        pen = QPen(QColor("#3d3d3d"))
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        
        # Yatay grid çizgileri (5 adet)
        for i in range(6):
            y_pos = y + (height * i / 5)
            painter.drawLine(x, int(y_pos), x + width, int(y_pos))
        
        # Dikey grid çizgileri (10 adet)
        for i in range(11):
            x_pos = x + (width * i / 10)
            painter.drawLine(int(x_pos), y, int(x_pos), y + height)
    
    def _draw_axes(self, painter, x, y, width, height):
        """Eksenleri ve etiketleri çizer."""
        pen = QPen(QColor("#e0e0e0"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Y ekseni
        painter.drawLine(x, y, x, y + height)
        
        # X ekseni
        painter.drawLine(x, y + height, x + width, y + height)
        
        # Y ekseni etiketleri
        font = QFont("Aptos Display", 9)
        painter.setFont(font)
        painter.setPen(QColor("#e0e0e0"))
        
        max_val = self.max_altitude if self.max_altitude > 0 else 100
        for i in range(6):
            value = max_val * (5 - i) / 5
            y_pos = y + (height * i / 5)
            painter.drawText(5, int(y_pos) + 5, f"{value:.0f}m")
        
        # X ekseni etiketi
        painter.drawText(x + width - 80, y + height + 30, f"Son {len(self.altitude_data)} veri")
    
    def _draw_data(self, painter, x, y, width, height):
        """Veri çizgisini çizer."""
        if len(self.altitude_data) < 2:
            return
        
        # Yeşil çizgi
        pen = QPen(QColor("#00ff00"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        max_val = self.max_altitude if self.max_altitude > 0 else 100
        data_list = list(self.altitude_data)
        
        # Noktalar arası çizgi çiz
        for i in range(len(data_list) - 1):
            x1 = x + (width * i / (len(data_list) - 1))
            y1 = y + height - (height * data_list[i] / max_val)
            
            x2 = x + (width * (i + 1) / (len(data_list) - 1))
            y2 = y + height - (height * data_list[i + 1] / max_val)
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Son noktayı vurgula
        last_x = x + width
        last_y = y + height - (height * data_list[-1] / max_val)
        painter.setBrush(QColor("#00ff00"))
        painter.drawEllipse(int(last_x - 4), int(last_y - 4), 8, 8)
        
        # Son değeri göster
        font = QFont("Aptos Display", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(int(last_x - 60), int(last_y - 10), f"{data_list[-1]:.1f}m")
    
    def clear_data(self):
        """Tüm veriyi temizler."""
        self.altitude_data.clear()
        self.max_altitude = 0
        self.update()
