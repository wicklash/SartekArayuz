"""
Sartek GCS - Configuration Module
Merkezi yapılandırma dosyası

Bu dosya, projedeki tüm sabit değerleri merkezi olarak yönetir.
Port numaraları, baud rate ve takım bilgileri gibi değerleri buradan değiştirebilirsiniz.
"""

import serial.tools.list_ports


# Seri Port Konfigürasyonu
# Not: GCS portu UI üzerinden kullanıcı tarafından seçilir

# Haberleşme Hızı (Baud Rate)
# Alıcı (Roket/Simülatör) ve Verici (Hakem) hızı ayrı ayrı ayarlanabilir
RECEIVER_BAUDRATE = 19200    # Roketten okuma hızı
TRANSMITTER_BAUDRATE = 19200 # Hakem arayüzüne gönderme hızı

# Takım Bilgileri
TEAM_ID = 1 # Takım numarası


def get_available_ports():
    """
    Sistemde mevcut seri portların listesini döndürür.
    
    Returns:
        list: Port isimlerinin listesi (örn: ['COM1', 'COM2', 'COM3'])
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]
