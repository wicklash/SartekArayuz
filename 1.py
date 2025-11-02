import serial
import time

# Portları listelemeye ÇALIŞMAYIN.
# İsimlerini bildiğimiz için doğrudan bağlanacağız.
port_adi = 'COM7'  # veya 'COM8'

try:
    print(f"{port_adi} portu açılmaya çalışılıyor...")
    
    # Not: Bu betiği çalıştırırken VS Code'u YÖNETİCİ olarak açmış olmalısınız.
    ser = serial.Serial(
        port=port_adi,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    
    print(f"BAŞARILI: {ser.port} portu açıldı.")
    
    # Portun gerçekten çalışıp çalışmadığını test edelim
    # (Bu kısım com0com'da portun diğer ucunu dinleyen bir şey varsa anlamlıdır)
    # ser.write(b'Merhaba\n')
    # time.sleep(0.1)
    # print(ser.readline())

    ser.close()
    print(f"{ser.port} portu kapatıldı.")

except serial.SerialException as e:
    print(f"HATA: {port_adi} portu açılamadı. Hata mesajı:")
    print(f" -> {e}")