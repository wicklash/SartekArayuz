# telemetry_grid_widget.py
# Telemetri veri kartları grid widget'ı

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class TelemetryGridWidget(QWidget):
    """
    Telemetri verilerini gösteren grid yapısı.
    21 adet veri kartı içerir.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_labels = {}  # Veri label'larını saklar
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Başlık
        self.section_label = QLabel("📊 Telemetri Verileri")
        self.section_label.setObjectName("section_title")
        
        # Grid layout
        self.data_grid = QGridLayout()
        self.data_grid.setSpacing(10)
        
        # Kartları oluştur ve yerleştir
        self._create_data_cards()
        
        layout.addWidget(self.section_label)
        layout.addLayout(self.data_grid)
    
    def _create_data_cards(self):
        """Tüm veri kartlarını oluşturur."""
        row = 0
        
        # Satır 1: Kimlik ve Paket
        self._add_card("🏷️ Takım ID", "takim_id", row, 0)
        self._add_card("📦 Paket Sayacı", "sayac", row, 1)
        self._add_card("📏 İrtifa (Barometrik)", "irtifa", row, 2)
        self._add_card("🎯 Durum", "durum", row, 3)
        
        row += 1
        # Satır 2: Ana Roket GPS
        self._add_card("🚀 Roket GPS İrtifa", "roket_gps_irtifa", row, 0)
        self._add_card("🚀 Roket Enlem", "roket_enlem", row, 1)
        self._add_card("🚀 Roket Boylam", "roket_boylam", row, 2, 1, 2)
        
        row += 1
        # Satır 3: Görev Yükü GPS
        self._add_card("📦 Görev Yükü GPS İrtifa", "gorev_gps_irtifa", row, 0)
        self._add_card("📦 Görev Yükü Enlem", "gorev_enlem", row, 1)
        self._add_card("📦 Görev Yükü Boylam", "gorev_boylam", row, 2, 1, 2)
        
        row += 1
        # Satır 4: Kademe GPS
        self._add_card("🔧 Kademe GPS İrtifa", "kademe_gps_irtifa", row, 0)
        self._add_card("🔧 Kademe Enlem", "kademe_enlem", row, 1)
        self._add_card("🔧 Kademe Boylam", "kademe_boylam", row, 2, 1, 2)
        
        row += 1
        # Satır 5: IMU Jiroskop
        self._add_card("🔄 Jiroskop X", "jiroskop_x", row, 0)
        self._add_card("🔄 Jiroskop Y", "jiroskop_y", row, 1)
        self._add_card("🔄 Jiroskop Z", "jiroskop_z", row, 2)
        self._add_card("📐 Açı", "aci", row, 3)
        
        row += 1
        # Satır 6: IMU İvme
        self._add_card("⚡ İvme X", "ivme_x", row, 0)
        self._add_card("⚡ İvme Y", "ivme_y", row, 1)
        self._add_card("⚡ İvme Z", "ivme_z", row, 2)
        self._add_card("✅ CRC", "crc", row, 3)
    
    def _add_card(self, title, key, row, col, rowspan=1, colspan=1):
        """
        Veri kartı ekler.
        
        Args:
            title: Kart başlığı
            key: Veri anahtarı (data_labels dict'inde kullanılır)
            row, col: Grid pozisyonu
            rowspan, colspan: Grid span değerleri
        """
        card = self._create_data_card(title)
        self.data_grid.addWidget(card['frame'], row, col, rowspan, colspan)
        self.data_labels[key] = card['value_label']
    
    def _create_data_card(self, title):
        """
        Tek bir veri kartı oluşturur.
        
        Returns:
            dict: 'frame' ve 'value_label' içeren dict
        """
        card = QFrame()
        card.setObjectName("data_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(3)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setObjectName("data_title")
        
        # Değer
        value_label = QLabel("-")
        value_label.setObjectName("data_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        return {
            'frame': card,
            'value_label': value_label
        }
    
    def update_data(self, telemetry_data):
        """
        Telemetri verisini gösterir.
        
        Args:
            telemetry_data: TelemetryData nesnesi
        """
        self.data_labels['takim_id'].setText(telemetry_data.takim_id)
        self.data_labels['sayac'].setText(telemetry_data.sayac)
        self.data_labels['irtifa'].setText(telemetry_data.irtifa)
        
        self.data_labels['roket_gps_irtifa'].setText(telemetry_data.roket_gps_irtifa)
        self.data_labels['roket_enlem'].setText(telemetry_data.roket_enlem)
        self.data_labels['roket_boylam'].setText(telemetry_data.roket_boylam)
        
        self.data_labels['gorev_gps_irtifa'].setText(telemetry_data.gorev_gps_irtifa)
        self.data_labels['gorev_enlem'].setText(telemetry_data.gorev_enlem)
        self.data_labels['gorev_boylam'].setText(telemetry_data.gorev_boylam)
        
        self.data_labels['kademe_gps_irtifa'].setText(telemetry_data.kademe_gps_irtifa)
        self.data_labels['kademe_enlem'].setText(telemetry_data.kademe_enlem)
        self.data_labels['kademe_boylam'].setText(telemetry_data.kademe_boylam)
        
        self.data_labels['jiroskop_x'].setText(telemetry_data.jiroskop_x)
        self.data_labels['jiroskop_y'].setText(telemetry_data.jiroskop_y)
        self.data_labels['jiroskop_z'].setText(telemetry_data.jiroskop_z)
        
        self.data_labels['ivme_x'].setText(telemetry_data.ivme_x)
        self.data_labels['ivme_y'].setText(telemetry_data.ivme_y)
        self.data_labels['ivme_z'].setText(telemetry_data.ivme_z)
        
        self.data_labels['aci'].setText(telemetry_data.aci)
        self.data_labels['durum'].setText(telemetry_data.durum_text)
        self.data_labels['crc'].setText(telemetry_data.crc)
