# data_log_window.py
# Detaylı veri log penceresi

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableView, QHeaderView, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from .telemetry_table_model import TelemetryTableModel
from .styles import DATA_LOG_WINDOW_STYLE, TABLE_VIEW_STYLE, CLEAR_BUTTON_STYLE
from ..core.config import get_resource_path


class DataLogWindow(QMainWindow):
    """
    Gelen ham telemetri verilerini detaylı gösteren ayrı pencere.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telemetri Veri Logları - Detaylı Görünüm")
        self.setWindowIcon(QIcon(get_resource_path("assets/icon.ico")))
        self.setGeometry(200, 200, 1000, 600)
        
        # Model'i oluştur (veriler burada tutulacak)
        self.model = TelemetryTableModel()
        
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
        self.clear_button.clicked.connect(self.clear_logs)
        self.clear_button.setStyleSheet(CLEAR_BUTTON_STYLE)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        
        # Tablo widget'ı (QTableView)
        self.table = QTableView()
        self.table.setModel(self.model)
        
        # Tablo stilleri
        # Tablo stilleri
        self.table.setStyleSheet(TABLE_VIEW_STYLE)
        
        # Sütun genişliklerini ayarla
        self.table.setColumnWidth(0, 50)  # Sıra numarası
        for i in range(1, 23):
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
        # Pencere stili
        self.setStyleSheet(DATA_LOG_WINDOW_STYLE)
    
    
    def add_log_entry(self, telemetry_data):
        """
        Model'e yeni veri ekler.
        """
        self.model.add_row(telemetry_data)
        
        # Eğer otomatik scroll isteniyorsa (veya kullanıcı en sondayken)
        if self.isVisible():
             self.table.scrollToBottom()

    def showEvent(self, event):
        """
        Pencere gösterildiğinde sona scroll et.
        """
        super().showEvent(event)
        self.table.scrollToBottom()
    
    def clear_logs(self):
        """Tüm log verilerini temizler."""
        self.model.clear()
