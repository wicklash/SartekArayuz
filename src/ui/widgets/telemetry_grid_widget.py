# telemetry_grid_widget.py
# Telemetri veri kartları grid widget'ı
# main.c yeni paket formatına göre güncellenmiştir.

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class TelemetryGridWidget(QWidget):
    """
    Telemetri verilerini gösteren grid yapısı.
    Yeni paket formatına göre:
    - Kademe GPS kartı kaldırıldı
    - Genel Bilgiler'den Takım ID kaldırıldı
    - Yeni 'GY Ortam Verileri' kartı eklendi (Basınç, Sıcaklık, Nem, Hes. İrtifa)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_labels = {}  # Veri label'larını saklar
        self.setMinimumHeight(380)  # Minimum 380px
        self.setMaximumHeight(480)  # Maksimum 480px
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

        # Satır 1: Genel Bilgiler | Roket GPS | Görev Yükü GPS | GY Ortam Verileri (2 satır dikey kapsar)
        self._add_multi_value_card("Genel Bilgiler",   ["sayac", "gorev_sayac", "irtifa", "durum", "crc"],  row, 0)
        self._add_multi_value_card("Roket GPS",        ["roket_gps_irtifa", "roket_enlem", "roket_boylam"],    row, 1)
        self._add_multi_value_card("Görev Yükü GPS",   ["gorev_gps_irtifa", "gorev_enlem", "gorev_boylam"],   row, 2)
        self._add_multi_value_card("GY Ortam Verileri",["gorev_basinc", "gorev_sicaklik", "gorev_hesaplanan_irtifa", "nem_label"], row, 3, 2, 1)  # dikey 2 satır kapla

        row += 1

        # Satır 2: Jiroskop | İvme | Açı (1 kolon)
        self._add_multi_value_card("Jiroskop", ["jiroskop_x", "jiroskop_y", "jiroskop_z"], row, 0)
        self._add_multi_value_card("İvme",     ["ivme_x", "ivme_y", "ivme_z"],             row, 1)
        self._add_card("Açı",  "aci",      row, 2, 1, 1)  # Açı kartı 1 kolon genişliğinde

    def _add_card(self, title, key, row, col, rowspan=1, colspan=1):
        """
        Tek değer kartı ekler.
        """
        card = self._create_data_card(title)
        self.data_grid.addWidget(card['frame'], row, col, rowspan, colspan)
        self.data_labels[key] = card['value_label']

    def _add_multi_value_card(self, title, keys, row, col, rowspan=1, colspan=1):
        """
        Çoklu değer kartı ekler.
        """
        card = QFrame()
        card.setObjectName("data_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)   # Dengeli iç boşluk
        card_layout.setSpacing(4)                    # Başlık ile değer arası dengeli boşluk
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # İçerikleri yukarı yasla

        # Başlık
        title_label = QLabel(title)
        title_label.setObjectName("data_title")
        card_layout.addWidget(title_label)

        # Varsayılan metin — içeriğe göre
        if "Genel" in title:
            default_text = "UKB Sayaç: -\nGY Sayaç: -\nİrtifa: -\nDurum: -\nCRC: -"
        elif "GPS" in title:
            default_text = "İrtifa: -\nEnlem: -\nBoylam: -"
        elif "Ortam" in title:
            default_text = "Hes. İrtifa: -\nBasınç: -\nSıcaklık: -\nNem: -\nYoğunluk: -"
        else:
            default_text = "X: -\nY: -\nZ: -"

        value_label = QLabel(default_text)
        value_label.setObjectName("data_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        card_layout.addWidget(value_label)

        self.data_grid.addWidget(card, row, col, rowspan, colspan)

        # Tüm key'ler aynı label'ı paylaşır
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
        card_layout.setContentsMargins(10, 8, 10, 8)   # Dengeli iç boşluk
        card_layout.setSpacing(4)                    # Başlık ile değer arası dengeli boşluk
        card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # İçerikleri yukarı yasla

        title_label = QLabel(title)
        title_label.setObjectName("data_title")

        value_label = QLabel("-")
        value_label.setObjectName("single_data_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Tekli değerleri ortala
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        return {'frame': card, 'value_label': value_label}

    def update_data(self, telemetry_data):
        """
        Telemetri verisini gösterir.
        UI katmanında formatlama yapılır (performans için).

        Args:
            telemetry_data: TelemetryData nesnesi
        """
        # Genel Bilgiler (UKB Sayaç, GY Sayaç, İrtifa, Durum, CRC)
        genel_text = (f"UKB Sayaç: {telemetry_data.sayac}\n"
                      f"GY Sayaç: {telemetry_data.gorev_sayac}\n"
                      f"İrtifa: {telemetry_data.get_formatted_irtifa()}\n"
                      f"Durum: {telemetry_data.durum_text}\n"
                      f"CRC: {telemetry_data.checksum}")
        self.data_labels['sayac'].setText(genel_text)

        # Roket GPS
        roket_gps_text = (f"İrtifa: {telemetry_data.get_formatted_gps_irtifa(telemetry_data.roket_gps_irtifa)}\n"
                          f"Enlem: {telemetry_data.get_formatted_coordinate(telemetry_data.roket_enlem)}\n"
                          f"Boylam: {telemetry_data.get_formatted_coordinate(telemetry_data.roket_boylam)}")
        self.data_labels['roket_gps_irtifa'].setText(roket_gps_text)

        # Görev Yükü GPS
        gorev_gps_text = (f"İrtifa: {telemetry_data.get_formatted_gps_irtifa(telemetry_data.gorev_gps_irtifa)}\n"
                          f"Enlem: {telemetry_data.get_formatted_coordinate(telemetry_data.gorev_enlem)}\n"
                          f"Boylam: {telemetry_data.get_formatted_coordinate(telemetry_data.gorev_boylam)}")
        self.data_labels['gorev_gps_irtifa'].setText(gorev_gps_text)

        # GY Ortam Verileri (Satır satır ayrı: Hes. İrtifa, Basınç, Sıcaklık, Nem, Yoğunluk)
        ortam_text = (f"Hes. İrtifa: {telemetry_data.get_formatted_calculated_altitude()}\n"
                      f"Basınç: {telemetry_data.get_formatted_pressure()}\n"
                      f"Sıcaklık: {telemetry_data.get_formatted_temperature()}\n"
                      f"Nem: {telemetry_data.get_formatted_humidity()}\n"
                      f"Yoğunluk: {telemetry_data.get_formatted_density()}")
        self.data_labels['gorev_basinc'].setText(ortam_text)

        # Jiroskop
        jiroskop_text = (f"X: {telemetry_data.get_formatted_gyro(telemetry_data.jiroskop_x)}\n"
                         f"Y: {telemetry_data.get_formatted_gyro(telemetry_data.jiroskop_y)}\n"
                         f"Z: {telemetry_data.get_formatted_gyro(telemetry_data.jiroskop_z)}")
        self.data_labels['jiroskop_x'].setText(jiroskop_text)

        # İvme
        ivme_text = (f"X: {telemetry_data.get_formatted_accel(telemetry_data.ivme_x)}\n"
                     f"Y: {telemetry_data.get_formatted_accel(telemetry_data.ivme_y)}\n"
                     f"Z: {telemetry_data.get_formatted_accel(telemetry_data.ivme_z)}")
        self.data_labels['ivme_x'].setText(ivme_text)

        # Açı
        self.data_labels['aci'].setText(telemetry_data.get_formatted_angle(telemetry_data.aci))
