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
        self.setMaximumHeight(450)  # Maksimum yükseklik 450px
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Başlık
        self.section_label = QLabel("Telemetri Verileri")
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
        
        # Satır 1: Kimlik, Paket, İrtifa ve Durum (birleşik kart)
        self._add_multi_value_card("Genel Bilgiler", ["takim_id", "sayac", "irtifa", "durum"], row, 0, 1, 1)
        
        # Satır 1: Roket GPS, Görev Yükü GPS ve Kademe GPS (yan yana)
        self._add_multi_value_card("Roket ", ["roket_gps_irtifa", "roket_enlem", "roket_boylam"], row, 1, 1, 1)
        self._add_multi_value_card("Görev Yükü ", ["gorev_gps_irtifa", "gorev_enlem", "gorev_boylam"], row, 2, 1, 1)
        self._add_multi_value_card("Kademe ", ["kademe_gps_irtifa", "kademe_enlem", "kademe_boylam"], row, 3, 1, 1)
        
        row += 1
        # Satır 2: Jiroskop, İvme, Açı ve CRC
        self._add_multi_value_card("Jiroskop", ["jiroskop_x", "jiroskop_y", "jiroskop_z"], row, 0, 1, 1)
        self._add_multi_value_card("İvme", ["ivme_x", "ivme_y", "ivme_z"], row, 1, 1, 1)
        self._add_card("Açı", "aci", row, 2, 1, 1)
        self._add_card("CRC", "crc", row, 3, 1, 1)
    
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
    
    def _add_multi_value_card(self, title, keys, row, col, rowspan=1, colspan=1):
        """
        Çoklu değer kartı ekler (GPS verileri için).
        
        Args:
            title: Kart başlığı
            keys: Veri anahtarları listesi [irtifa, enlem, boylam]
            row, col: Grid pozisyonu
            rowspan, colspan: Grid span değerleri
        """
        card = QFrame()
        card.setObjectName("data_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(4, 2, 4, 2)
        card_layout.setSpacing(2)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setObjectName("data_title")
        card_layout.addWidget(title_label)
        
        # Değer label'ı - içeriğe göre
        if "Genel Bilgiler" in title:
            default_text = "Takım ID: -\nPaket: -\nİrtifa: -\nDurum: -"
        elif "gps" in title.lower():
            default_text = "İrtifa: -\nEnlem: -\nBoylam: -"
        else:
            default_text = "X: -\nY: -\nZ: -"
        
        value_label = QLabel(default_text)
        value_label.setObjectName("data_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        value_label.setStyleSheet("font-size: 13px; line-height: 1.3;")
        card_layout.addWidget(value_label)
        
        self.data_grid.addWidget(card, row, col, rowspan, colspan)
        
        # Her bir key için aynı label'ı sakla
        for key in keys:
            self.data_labels[key] = value_label
    
    def _create_data_card(self, title):
        """
        Tek bir veri kartı oluşturur.
        
        Returns:
            dict: 'frame' ve 'value_label' içeren dict
        """
        card = QFrame()
        card.setObjectName("data_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(4, 2, 4, 2)
        card_layout.setSpacing(1)
        
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
        UI katmanında formatlama yapılır (performans için).
        
        Args:
            telemetry_data: TelemetryData nesnesi (saf sayı değerler içerir)
        """
        # Genel Bilgiler (birleşik)
        genel_text = (f"Takım ID: {telemetry_data.takim_id}\n"
                     f"Paket: {telemetry_data.sayac}\n"
                     f"İrtifa: {telemetry_data.get_formatted_irtifa()}\n"
                     f"Durum: {telemetry_data.durum_text}")
        self.data_labels['takim_id'].setText(genel_text)
        
        # Roket GPS (birleşik)
        roket_gps_text = (f"İrtifa: {telemetry_data.get_formatted_gps_irtifa(telemetry_data.roket_gps_irtifa)}\n"
                         f"Enlem: {telemetry_data.get_formatted_coordinate(telemetry_data.roket_enlem)}\n"
                         f"Boylam: {telemetry_data.get_formatted_coordinate(telemetry_data.roket_boylam)}")
        self.data_labels['roket_gps_irtifa'].setText(roket_gps_text)
        
        # Görev Yükü GPS (birleşik)
        gorev_gps_text = (f"İrtifa: {telemetry_data.get_formatted_gps_irtifa(telemetry_data.gorev_gps_irtifa)}\n"
                         f"Enlem: {telemetry_data.get_formatted_coordinate(telemetry_data.gorev_enlem)}\n"
                         f"Boylam: {telemetry_data.get_formatted_coordinate(telemetry_data.gorev_boylam)}")
        self.data_labels['gorev_gps_irtifa'].setText(gorev_gps_text)
        
        # Kademe GPS (birleşik)
        kademe_gps_text = (f"İrtifa: {telemetry_data.get_formatted_gps_irtifa(telemetry_data.kademe_gps_irtifa)}\n"
                          f"Enlem: {telemetry_data.get_formatted_coordinate(telemetry_data.kademe_enlem)}\n"
                          f"Boylam: {telemetry_data.get_formatted_coordinate(telemetry_data.kademe_boylam)}")
        self.data_labels['kademe_gps_irtifa'].setText(kademe_gps_text)
        
        # Jiroskop (birleşik)
        jiroskop_text = (f"X: {telemetry_data.get_formatted_gyro(telemetry_data.jiroskop_x)}\n"
                        f"Y: {telemetry_data.get_formatted_gyro(telemetry_data.jiroskop_y)}\n"
                        f"Z: {telemetry_data.get_formatted_gyro(telemetry_data.jiroskop_z)}")
        self.data_labels['jiroskop_x'].setText(jiroskop_text)
        
        # İvme (birleşik)
        ivme_text = (f"X: {telemetry_data.get_formatted_accel(telemetry_data.ivme_x)}\n"
                    f"Y: {telemetry_data.get_formatted_accel(telemetry_data.ivme_y)}\n"
                    f"Z: {telemetry_data.get_formatted_accel(telemetry_data.ivme_z)}")
        self.data_labels['ivme_x'].setText(ivme_text)
        
        # Açı
        self.data_labels['aci'].setText(telemetry_data.get_formatted_angle(telemetry_data.aci))
        
        # Checksum
        self.data_labels['crc'].setText(str(telemetry_data.checksum))
