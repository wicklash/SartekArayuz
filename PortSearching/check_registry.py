import winreg

print("Python 'winreg' modülü ile kayıt defteri okunuyor...")
print("Adres: HKLM\\HARDWARE\\DEVICEMAP\\SERIALCOMM")
print("-" * 20)

port_listesi = {}

try:
    # 64-bit (Standart) kayıt defteri görünümünü aç
    key_path = r"HARDWARE\DEVICEMAP\SERIALCOMM"
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
    
    print("--- 64-bit (KEY_WOW64_64KEY) Görünümü ---")
    i = 0
    while True:
        try:
            value_name, value_data, value_type = winreg.EnumValue(key, i)
            print(f"  {value_name} : {value_data}")
            port_listesi[value_data] = value_name
            i += 1
        except OSError:
            break # Değer kalmadı
    winreg.CloseKey(key)

except Exception as e:
    print(f"64-bit anahtar okunurken hata: {e}")

print("-" * 20)

# Bir de 32-bit (WoW) kayıt defteri görünümüne bakalım
try:
    key_path = r"HARDWARE\DEVICEMAP\SERIALCOMM"
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
    
    print("--- 32-bit (KEY_WOW64_32KEY) Görünümü ---")
    i = 0
    while True:
        try:
            value_name, value_data, value_type = winreg.EnumValue(key, i)
            print(f"  {value_name} : {value_data}")
            port_listesi[value_data] = value_name # Aynı listeye ekle
            i += 1
        except OSError:
            break # Değer kalmadı
    winreg.CloseKey(key)

except Exception as e:
    print(f"32-bit anahtar okunurken hata: {e}")


print("\n=== Toplam Bulunan Portlar ===")
if not port_listesi:
    print("Hiç port bulunamadı.")
else:
    for port, device in port_listesi.items():
        print(f"  {port} ({device})")