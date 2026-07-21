
from PyQt6.QtCore import QAbstractTableModel, Qt
from ..core.data_parser import TelemetryData

class TelemetryTableModel(QAbstractTableModel):
    """
    Telemetri verilerini QTableView için sağlayan model.
    Verileri kopyalamaz, mevcut listeyi referans alır.
    Sanallaştırma (virtualization) sayesinde binlerce satırı dondurmadan gösterir.
    Yeni paket formatına göre güncellenmiştir:
    - "Takım ID" yerine "Nem (%)"
    - "Kademe GPS ..." sütunları yerine "GY Basınç", "GY Sıcaklık", "GY Hes. İrtifa"
    """

    HEADERS = [
        "Sıra No", "UKB Sayaç", "GY Sayaç", "Nem (%)", "İrtifa",
        "Roket GPS İrtifa", "Roket Enlem", "Roket Boylam",
        "Görev GPS İrtifa", "Görev Enlem", "Görev Boylam",
        "GY Basınç (Pa)", "GY Sıcaklık (°C)", "GY Hes. İrtifa", "GY Yoğunluk (kg/m³)",
        "Jiroskop X", "Jiroskop Y", "Jiroskop Z",
        "İvme X", "İvme Y", "İvme Z",
        "Açı", "Durum", "CRC"
    ]

    def __init__(self, data_list=None):
        super().__init__()
        self._data = data_list if data_list is not None else []

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()

            if row >= len(self._data):
                return None

            telemetry: TelemetryData = self._data[row]

            if col == 0:  return str(row + 1)                                                   # Sıra No
            if col == 1:  return str(telemetry.sayac)                                            # UKB Sayaç
            if col == 2:  return str(telemetry.gorev_sayac)                                      # GY Sayaç
            if col == 3:  return str(telemetry.nem)                                              # Nem (%)
            if col == 4:  return telemetry.get_formatted_irtifa()                                # İrtifa
            if col == 5:  return telemetry.get_formatted_gps_irtifa(telemetry.roket_gps_irtifa)  # Roket GPS İrtifa
            if col == 6:  return telemetry.get_formatted_coordinate(telemetry.roket_enlem)       # Roket Enlem
            if col == 7:  return telemetry.get_formatted_coordinate(telemetry.roket_boylam)      # Roket Boylam
            if col == 8:  return telemetry.get_formatted_gps_irtifa(telemetry.gorev_gps_irtifa)  # Görev GPS İrtifa
            if col == 9:  return telemetry.get_formatted_coordinate(telemetry.gorev_enlem)       # Görev Enlem
            if col == 10: return telemetry.get_formatted_coordinate(telemetry.gorev_boylam)      # Görev Boylam
            if col == 11: return telemetry.get_formatted_pressure()                              # GY Basınç
            if col == 12: return telemetry.get_formatted_temperature()                           # GY Sıcaklık
            if col == 13: return telemetry.get_formatted_calculated_altitude()                   # GY Hesaplanan İrtifa
            if col == 14: return telemetry.get_formatted_density()                               # GY Yoğunluk
            if col == 15: return telemetry.get_formatted_gyro(telemetry.jiroskop_x)             # Jiro X
            if col == 16: return telemetry.get_formatted_gyro(telemetry.jiroskop_y)             # Jiro Y
            if col == 17: return telemetry.get_formatted_gyro(telemetry.jiroskop_z)             # Jiro Z
            if col == 18: return telemetry.get_formatted_accel(telemetry.ivme_x)                # İvme X
            if col == 19: return telemetry.get_formatted_accel(telemetry.ivme_y)                # İvme Y
            if col == 20: return telemetry.get_formatted_accel(telemetry.ivme_z)                # İvme Z
            if col == 21: return telemetry.get_formatted_angle(telemetry.aci)                   # Açı
            if col == 22: return telemetry.durum_text                                            # Durum
            if col == 23: return str(telemetry.checksum)                                         # CRC

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if 0 <= section < len(self.HEADERS):
                    return self.HEADERS[section]
        return None

    def add_row(self, telemetry_data):
        """Yeni veri ekler ve tabloyu günceller."""
        position = len(self._data)
        self.beginInsertRows(self.index(0, 0).parent(), position, position)
        self._data.append(telemetry_data)
        self.endInsertRows()

    def clear(self):
        """Tüm veriyi siler."""
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()
