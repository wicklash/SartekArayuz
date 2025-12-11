"""
Sartek GCS - Configuration Module
Merkezi yapılandırma dosyası

Bu dosya, projedeki tüm sabit değerleri merkezi olarak yönetir.
Port numaraları, baud rate ve takım bilgileri gibi değerleri buradan değiştirebilirsiniz.
"""

import serial.tools.list_ports


# Seri Port Konfigürasyonu
# Roket Simülatörü - Simülatörün yazacağı port
# Not: GCS portu UI üzerinden kullanıcı tarafından seçilir
SERIAL_PORT_ROCKET = 'COM9'

# Haberleşme Hızı (Baud Rate)
BAUDRATE = 19200

# Takım Bilgileri
TEAM_ID = 123456  # Takım numarası


def get_available_ports():
    """
    Sistemde mevcut seri portların listesini döndürür.
    
    Returns:
        list: Port isimlerinin listesi (örn: ['COM1', 'COM2', 'COM3'])
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]
