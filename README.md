# Sartek GCS - Roket Telemetri Sistemi

Modern PyQt6 tabanlı yer kontrol istasyonu uygulaması.

## Özellikler

- 🚀 Gerçek zamanlı telemetri veri görüntüleme
- 📊 İrtifa grafiği
- 📡 Seri port üzerinden veri alımı
- 🎮 Simülatör kontrolü
- 📝 Detaylı veri log penceresi
- 🎨 Modern dark tema arayüz

## 🛠 Kurulum Adımları

Uygulamayı çalıştırmak için aşağıdaki adımları sırasıyla terminale/komut satırına yazmanız yeterlidir:

**1. Adım: Sanal Ortam Oluşturun**
Projenin bağımlılıklarını bilgisayarınızdaki diğer projelerden ayırmak için bir izolasyon alanı oluşturuyoruz:
```bash
python -m venv .venv
```

**2. Adım: Sanal Ortamı Aktifleştirin**
Oluşturduğumuz bu alanı kullanıma açıyoruz (Windows için):
```bash
.venv\Scripts\activate
```
*Not: Başarıyla bağlandığınızda terminal satırının başında `(.venv)` ifadesini görmelisiniz.*

**3. Adım: Gerekli Paketleri Yükleyin**
Arayüzün ve araçların çalışması için gereken tüm kütüphaneleri otomatik olarak yüklüyoruz:
```bash
pip install -r requirements.txt
```

## 🚀 Çalıştırma

Kurulum tamamlandıktan sonra uygulamayı ve test simülatörünü başlatabilirsiniz:

1.  **Ana Arayüzü Başlatma:**
    ```bash
    python main.py
    ```


## Yapı

```
SartekArayüz/
├── assets/              # İkonlar ve görseller
├── src/
│   ├── core/           # İş mantığı
│   │   ├── data_parser.py
│   │   ├── serial_manager.py
│   │   ├── serial_worker.py
│   │   └── simulator_manager.py
│   └── ui/             # Kullanıcı arayüzü
│       ├── widgets/    # UI bileşenleri
│       ├── main_window.py
│       ├── data_log_window.py
│       └── styles.py
├── main.py             # Ana giriş noktası
└── simulator.py        # Test simülatörü
```


## İletişim Protokolü (Binary)

Sistem, 78 byte uzunluğunda sabit bir veri paketi kullanır:

| Byte | İçerik | Tip | Açıklama |
|------|--------|-----|----------|
| 0-3 | Header | - | `FF FF 54 52` |
| 4 | Takım ID | UINT8 | Takım ID (Low Byte) |
| 5 | Sayaç | UINT8 | 0-255 Döngüsel |
| 6-73 | Payload | Float32 | *Aşağıdaki tabloya bakınız* |
| 74 | Durum | UINT8 | 0:Uçuşa Hazırlık, 1:Uçuş, 2:Apogee, 3:1.Ayrılma, 4:2.Ayrılma, 5:İniş |
| 75 | Checksum | UINT8 | Modulo 256 |
| 76-77| Footer | - | `0D 0A` (\r\n) |

**Payload (Float32 - Little Endian):**
İrtifa, Roket GPS (İrt, Enl, Boy), Görev Yükü GPS (İrt, Enl, Boy), Kademe GPS (İrt, Enl, Boy), Jiro (X,Y,Z), İvme (X,Y,Z), Açı.

## Log Dosyası Formatı (CSV)

Uygulama verileri `logs/` klasörüne CSV formatında kaydeder:
```csv
Zaman,TakimID,Sayac,Irtifa,
Roket_GPS_Irtifa,Roket_Enlem,Roket_Boylam,
Gorev_GPS_Irtifa,Gorev_Enlem,Gorev_Boylam,
Kademe_GPS_Irtifa,Kademe_Enlem,Kademe_Boylam,
Jiro_X,Jiro_Y,Jiro_Z,
Ivme_X,Ivme_Y,Ivme_Z,
Aci,Durum,Durum_Metin,Checksum
```

## Konfigürasyon

Tüm ayarlar `src/core/config.py` dosyasında bulunur:

```python
# src/core/config.py

# Seri Haberleşme Hızları
RECEIVER_BAUDRATE = 19200    # Roketten gelen veri hızı
TRANSMITTER_BAUDRATE = 19200 # Hakem sunucusuna giden veri hızı

# Takım Ayarları
TEAM_ID = 123456
```

## Lisans

MIT

Görselleştirme ve Yer Kontrol Yazılımı
Geliştirilen yer istasyonu arayüz yazılımı; Python tabanlı PyQt6 mimarisiyle, düşük gecikmeli veri işleme ve anlık görselleştirme odağında tasarlanmıştır. Yazılımın temel özellikleri şunlardır:

Performanslı Grafikleme: PyQtGraph ve NumPy entegrasyonu ile irtifa ve sensör verileri gerçek zamanlı, yüksek FPS değerlerinde çizdirilir.

Asenkron Veri Akışı: QThread yapısı sayesinde seri port (pyserial) okumaları arayüzden bağımsız yürütülerek donma yaşanması engellenir.

Hata Denetimi ve Loglama: Gelen 78 byte'lık ham paketler data_parser ile çözümlenir, doğrulanır ve eşzamanlı olarak CSV formatında kaydedilir.

