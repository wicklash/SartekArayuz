from PyQt6.QtCore import QAbstractTableModel, Qt
from ..core.data_parser import TelemetryData

class TelemetryTableModel(QAbstractTableModel):
    """
    Telemetri verilerini QTableView için sağlayan model.
    Verileri kopyalamaz, mevcut listeyi referans alır.
    Sanallaştırma (virtualization) sayesinde binlerce satırı dondurmadan gösterir.
    """
    
    HEADERS = [
        "Zaman", "Takım ID", "Sayac", "İrtifa", 
        "Roket GPS İrtifa", "Roket Enlem", "Roket Boylam",
        "Görev GPS İrtifa", "Görev Enlem", "Görev Boylam",
        "Kademe GPS İrtifa", "Kademe Enlem", "Kademe Boylam",
        "Jiroskop X", "Jiroskop Y", "Jiroskop Z",
        "İvme X", "İvme Y", "İvme Z",
        "Açı", "Durum", "CRC"
    ]

    def __init__(self, data_list=None):
        super().__init__()
        self._data = data_list if data_list is not None else []
        self._formatted_cache = {} # Opsiyonel: Formatlama işlemini cachelemek için

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
            
            # Liste sınır kontrolü
            if row >= len(self._data):
                return None
                
            telemetry: TelemetryData = self._data[row]
            
            # Sütunlara göre veri map'lemesi
            # Not: TelemetryData içinde 'timestamp' henüz yok, o yüzden '-' veriyoruz veya eklemeliyiz
            # CSVLogger'da ekledik ama TelemetryData class'ında field yok. 
            # Şimdilik sadece index numarası verelim Zaman yerine, veya sırasını düzeltelim.
            
            if col == 0: return str(row + 1) # Sıra No
            if col == 1: return str(telemetry.takim_id)
            if col == 2: return str(telemetry.sayac)
            if col == 3: return telemetry.get_formatted_irtifa()
            if col == 4: return telemetry.get_formatted_gps_irtifa(telemetry.roket_gps_irtifa)
            if col == 5: return telemetry.get_formatted_coordinate(telemetry.roket_enlem)
            if col == 6: return telemetry.get_formatted_coordinate(telemetry.roket_boylam)
            if col == 7: return telemetry.get_formatted_gps_irtifa(telemetry.gorev_gps_irtifa)
            if col == 8: return telemetry.get_formatted_coordinate(telemetry.gorev_enlem)
            if col == 9: return telemetry.get_formatted_coordinate(telemetry.gorev_boylam)
            if col == 10: return telemetry.get_formatted_gps_irtifa(telemetry.kademe_gps_irtifa)
            if col == 11: return telemetry.get_formatted_coordinate(telemetry.kademe_enlem)
            if col == 12: return telemetry.get_formatted_coordinate(telemetry.kademe_boylam)
            if col == 13: return telemetry.get_formatted_gyro(telemetry.jiroskop_x)
            if col == 14: return telemetry.get_formatted_gyro(telemetry.jiroskop_y)
            if col == 15: return telemetry.get_formatted_gyro(telemetry.jiroskop_z)
            if col == 16: return telemetry.get_formatted_accel(telemetry.ivme_x)
            if col == 17: return telemetry.get_formatted_accel(telemetry.ivme_y)
            if col == 18: return telemetry.get_formatted_accel(telemetry.ivme_z)
            if col == 19: return telemetry.get_formatted_angle(telemetry.aci)
            if col == 20: return telemetry.durum_text
            if col == 21: return str(telemetry.checksum)

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if 0 <= section < len(self.HEADERS):
                    return self.HEADERS[section]
            # Dikey header (satır numaraları) kapalı olacak ama yine de döndürebiliriz
            
        return None

    def add_row(self, telemetry_data):
        """
        Yeni veri ekler ve tabloyu günceller.
        """
        # Listenin sonuna satır eklendiğini bildir
        position = len(self._data)
        self.beginInsertRows(self.index(0, 0).parent(), position, position)
        
        self._data.append(telemetry_data)
        
        self.endInsertRows()

    def clear(self):
        """
        Tüm veriyi siler.
        """
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()
