# Sartek GCS - Roket Telemetri Sistemi

Modern PyQt6 tabanlı yer kontrol istasyonu uygulaması.

## Özellikler

- 🚀 Gerçek zamanlı telemetri veri görüntüleme
- 📊 İrtifa grafiği
- 📡 Seri port üzerinden veri alımı
- 🎮 Simülatör kontrolü
- 📝 Detaylı veri log penceresi
- 🎨 Modern dark tema arayüz

## Kurulum

```bash
# Sanal ortam oluştur
python -m venv .venv

# Sanal ortamı aktifleştir (Windows)
.venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

## Kullanım

```bash
# Uygulamayı başlat
python main.py

# Simülatörü ayrı bir terminalde çalıştır
python simulator.py
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

## Telemetri Veri Formatı

CSV formatında 21 alan:
```
TAKIM_ID,SAYAC,IRTIFA,ROKET_GPS_IRT,ROKET_ENLEM,ROKET_BOYLAM,
GOREV_GPS_IRT,GOREV_ENLEM,GOREV_BOYLAM,KADEME_GPS_IRT,KADEME_ENLEM,KADEME_BOYLAM,
JIRO_X,JIRO_Y,JIRO_Z,IVME_X,IVME_Y,IVME_Z,ACI,DURUM,CRC
```

## Konfigürasyon

`main.py` içinde:
```python
GCS_PORT = 'COM8'  # GCS dinleme portu
BAUDRATE = 9600    # İletişim hızı
```

## Lisans

MIT
