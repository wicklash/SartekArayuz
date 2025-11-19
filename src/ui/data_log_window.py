# data_log_window.py
# Detaylı veri log penceresi

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DataLogWindow(QMainWindow):
    """
    Gelen ham telemetri verilerini detaylı gösteren ayrı pencere.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telemetri Veri Logları - Detaylı Görünüm")
        self.setGeometry(200, 200, 1000, 600)
        self.log_data = []  # Tüm log verilerini saklar
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Üst buton satırı
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Temizle")
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #ef5350;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        
        # Tablo widget'ı
        self.table = QTableWidget()
        self.table.setColumnCount(22)  # Sıra numarası + 21 telemetri alanı
        
        # Sütun başlıkları
        headers = [
            "#", "Takım ID", "Sayac", "İrtifa", "Roket GPS İrtifa", "Roket Enlem", "Roket Boylam",
            "Görev GPS İrtifa", "Görev Enlem", "Görev Boylam", "Kademe GPS İrtifa", 
            "Kademe Enlem", "Kademe Boylam", "Jiroskop X", "Jiroskop Y", "Jiroskop Z",
            "İvme X", "İvme Y", "İvme Z", "Açı", "Durum", "CRC"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Tablo stilleri
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                gridline-color: #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #4d4d4d;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #3d3d3d;
                font-weight: 700;
                font-size: 10px;
                text-transform: uppercase;
            }
        """)
        
        # Sütun genişliklerini ayarla
        self.table.setColumnWidth(0, 50)  # Sıra numarası
        for i in range(1, 22):
            self.table.setColumnWidth(i, 100)
        
        # Header boyutlandırma
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Dikey header'ı gizle
        self.table.verticalHeader().setVisible(False)
        
        # Alternating row colors
        self.table.setAlternatingRowColors(True)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        
        # Pencere stili
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
        """)
    
    def add_log_entry(self, telemetry_data):
        """
        Tabloya yeni veri satırı ekler.
        
        Args:
            telemetry_data: TelemetryData nesnesi
        """
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # Sıra numarası
        item = QTableWidgetItem(str(row_position + 1))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_position, 0, item)
        
        # Telemetri verileri
        data_items = [
            telemetry_data.takim_id,
            telemetry_data.sayac,
            telemetry_data.irtifa,
            telemetry_data.roket_gps_irtifa,
            telemetry_data.roket_enlem,
            telemetry_data.roket_boylam,
            telemetry_data.gorev_gps_irtifa,
            telemetry_data.gorev_enlem,
            telemetry_data.gorev_boylam,
            telemetry_data.kademe_gps_irtifa,
            telemetry_data.kademe_enlem,
            telemetry_data.kademe_boylam,
            telemetry_data.jiroskop_x,
            telemetry_data.jiroskop_y,
            telemetry_data.jiroskop_z,
            telemetry_data.ivme_x,
            telemetry_data.ivme_y,
            telemetry_data.ivme_z,
            telemetry_data.aci,
            telemetry_data.durum_text,
            telemetry_data.crc
        ]
        
        for col, data in enumerate(data_items, start=1):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_position, col, item)
        
        # Otomatik scroll (en sona git)
        self.table.scrollToBottom()
    
    def clear_logs(self):
        """Tüm log verilerini temizler."""
        self.table.setRowCount(0)
        self.log_data.clear()
