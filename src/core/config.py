"""
Sartek GCS - Configuration Module
Merkezi yapılandırma dosyası

Bu dosya, projedeki tüm sabit değerleri merkezi olarak yönetir.
Port numaraları, baud rate ve takım bilgileri gibi değerleri buradan değiştirebilirsiniz.
"""

# Seri Port Konfigürasyonu
# GCS (Ground Control Station) - Yer istasyonunun dinleyeceği port
SERIAL_PORT_GCS = 'COM1'

# Roket Simülatörü - Simülatörün yazacağı port
SERIAL_PORT_ROCKET = 'COM2'

# Haberleşme Hızı (Baud Rate)
BAUDRATE = 9600

# Takım Bilgileri
TEAM_ID = 123456  # Takım numarası
