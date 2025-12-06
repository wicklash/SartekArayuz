# altitude_chart_widget.py
# Roket irtifa grafiği widget'ı
# pyqtgraph kullanarak yüksek performanslı gerçek zamanlı grafik

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from collections import deque
import pyqtgraph as pg
import numpy as np


class AltitudeChartWidget(QWidget):
    """
    Roket irtifa verilerini gösteren gerçek zamanlı grafik.
    pyqtgraph kullanarak yüksek performanslı çizim sağlar.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Son 100 veri noktasını tutmak için deque kullanılıyor
        self.altitude_data = deque(maxlen=100)
        self.max_altitude = 0
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır ve pyqtgraph PlotWidget'ını hazırlar."""
        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Başlık
        self.title_label = QLabel("Gerçek Zamanlı İrtifa Grafiği")
        self.title_label.setObjectName("section_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 11px; padding: 2px;")  # Başlık boyutunu küçült
        layout.addWidget(self.title_label)
        
        # pyqtgraph PlotWidget oluştur
        self.plot_widget = pg.PlotWidget()
        
        # Performans optimizasyonları (50Hz+ veri akışı için kritik)
        self.plot_widget.setClipToView(True)  # Sadece ekranda görünen kısmı çiz
        self.plot_widget.setDownsampling(True)  # Veri sıkıştırma/seyreltme aktif
        
        # Görsel tasarım ayarları
        # Arka plan rengi: koyu gri (#2d2d2d)
        self.plot_widget.setBackground('#2d2d2d')
        
        # Grid (Izgara) ayarları - X ve Y eksenlerinde açık
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Zoom ve Pan özelliklerini aktif et
        self.plot_widget.setMouseEnabled(x=True, y=True)  # Pan için
        # Zoom için varsayılan davranış zaten aktif (sağ tık + sürükle)
        
        # Eksen etiketleri
        self.plot_widget.setLabel('left', 'İrtifa (m)', color='#e0e0e0')
        self.plot_widget.setLabel('bottom', 'Zaman (veri noktası)', color='#e0e0e0')
        
        # Eksen renkleri
        self.plot_widget.getAxis('left').setPen(pg.mkPen('#e0e0e0', width=1))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen('#e0e0e0', width=1))
        
        # Grafik çizgisi oluştur - Parlak Yeşil (#00ff00), 2px kalınlık
        self.plot_curve = self.plot_widget.plot(
            pen=pg.mkPen('#00ff00', width=2),
            name='İrtifa'
        )
        
        # Başlangıçta boş veri seti
        self.plot_curve.setData([], [])
        
        layout.addWidget(self.plot_widget)
        
        # Minimum boyut - küçültülmüş
        self.setMinimumHeight(200)
    
    def add_altitude(self, altitude_value):
        """
        Yeni irtifa verisi ekler.
        
        Performans optimizasyonu: Direkt float değer alır, string parsing yapmaz.
        
        Args:
            altitude_value: İrtifa değeri (float)
        """
        try:
            # Veriyi deque'ye ekle (zaten float)
            self.altitude_data.append(float(altitude_value))
            
            # Maksimum irtifayı güncelle
            if altitude_value > self.max_altitude:
                self.max_altitude = altitude_value
            
            # Grafik güncellemesi - Tüm grafiği silip yeniden çizmek yerine
            # sadece veri setini (setData) güncelle (performans için kritik)
            self._update_plot()
            
        except (ValueError, TypeError, AttributeError):
            # Hatalı veri geldiğinde sessizce atla
            pass
    
    def _update_plot(self):
        """
        Grafik verisini günceller.
        setData kullanarak yüksek performanslı güncelleme yapar.
        """
        if len(self.altitude_data) == 0:
            self.plot_curve.setData([], [])
            return
        
        # Veriyi numpy array'e çevir (pyqtgraph için optimize)
        data_list = list(self.altitude_data)
        x_data = np.arange(len(data_list))  # X ekseni: veri noktası indeksleri
        y_data = np.array(data_list)  # Y ekseni: irtifa değerleri
        
        # setData ile güncelleme (tüm grafiği silip yeniden çizmek yerine)
        # Bu yaklaşım yüksek frekanslı veri akışında çok daha performanslıdır
        self.plot_curve.setData(x_data, y_data)
        
        # Y ekseni aralığını dinamik olarak ayarla
        if self.max_altitude > 0:
            # Maksimum değerin %10 fazlası kadar üst boşluk bırak
            self.plot_widget.setYRange(0, self.max_altitude * 1.1, padding=0.05)
        else:
            # Varsayılan aralık
            self.plot_widget.setYRange(0, 100, padding=0.05)
        
        # X ekseni aralığını ayarla (tüm veriyi göster)
        if len(data_list) > 1:
            self.plot_widget.setXRange(0, len(data_list) - 1, padding=0.05)
    
    def clear_data(self):
        """Tüm veriyi temizler ve grafiği sıfırlar."""
        self.altitude_data.clear()
        self.max_altitude = 0
        self.plot_curve.setData([], [])