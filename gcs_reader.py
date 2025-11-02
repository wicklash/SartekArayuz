# gcs_reader.py
# Bu, pyserial, PyQt6 ve QThread kullanan Yer Kontrol İstasyonu uygulamasıdır.
# DOĞRUDAN COM8 portunu dinler.

import sys
import serial
# import serial.tools.list_ports # <--- DEĞİŞİKLİK: Artık kullanılmıyor.
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QTextEdit, QPushButton, QLabel, QHBoxLayout # <--- DEĞİŞİKLİK: QComboBox kaldırıldı
)
# 'Qt' modülü import edildi
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QCoreApplication, Qt 

# --- Worker Sınıfı (Seri Port Okuma için) ---
# QObject'ten miras alır, böylece QThread'e taşınabilir.
class SerialWorker(QObject):
    """
    GUI'yi bloke etmemek için ayrı bir thread'de seri port okuması yapar.
    """
    # GUI thread'ine göndermek için sinyaller
    data_received = pyqtSignal(str)  # Gelen veriyi (string) gönderir
    port_error = pyqtSignal(str)     # Hata mesajı gönderir
    finished = pyqtSignal()          # Thread bittiğinde sinyal verir

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.is_running = False
        self.ser = None

    def run(self):
        """
        Thread başlatıldığında çalışacak ana fonksiyon.
        """
        self.is_running = True
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Worker: {self.port} portu açıldı.")
        except serial.SerialException as e:
            self.port_error.emit(f"Port açılamadı: {e}")
            self.is_running = False
            self.finished.emit() # Hata durumunda da thread'in bittiğini bildir
            return

        while self.is_running:
            try:
                # ser.readline() burada bekler (timeout=1 saniye)
                # GUI thread'ini bloke etmez, çünkü bu 'run' metodu
                # ayrı bir QThread'de çalışır.
                if self.ser.in_waiting > 0:
                    line_bytes = self.ser.readline()
                    
                    # Gelen byte'ları UTF-8 string'e çevir
                    try:
                        line_str = line_bytes.decode('utf-8').strip()
                        if line_str:
                            # Veri alındıysa, GUI'ye sinyal gönder
                            self.data_received.emit(line_str)
                    except UnicodeDecodeError:
                        # Hatalı veri gelirse (örn: bağlantı yeni kurulurken)
                        print("Worker: Hatalı byte dizisi alındı, atlanıyor.")

            except serial.SerialException as e:
                # Cihaz çıkarılırsa vb.
                self.port_error.emit(f"Seri port hatası: {e}")
                self.is_running = False
            
            # Ana thread'den (GUI) durdurma sinyali gelirse döngüden çık
            if not self.is_running:
                break
        
        # Döngü bittiğinde portu kapat
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Worker: {self.port} portu kapatıldı.")
        
        self.finished.emit() # Thread'in işini bitirdiğini bildir

    def stop(self):
        """
        Thread'in güvenli bir şekilde durdurulması için 'is_running' flag'ını ayarlar.
        """
        self.is_running = False
        print("Worker: Durdurma sinyali alındı.")


# --- Ana Arayüz Sınıfı ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sartek GCS - Serial Test")
        self.setGeometry(100, 100, 600, 400)

        # Thread ve Worker için referanslar
        self.serial_thread = None
        self.serial_worker = None

        # Arayüz Bileşenleri
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        
        # <--- DEĞİŞİKLİK: Port seçim alanı kaldırıldı, yerine sabit bir etiket eklendi ---
        # Port seçim alanı
        self.port_label = QLabel(f"Hedef Port: {GCS_PORT} (Sabit)")
        self.port_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Metni ortala
        # -----------------------------------------------------------------------------
        
        # Bağlantı Butonları
        self.connect_button = QPushButton("Bağlan")
        self.disconnect_button = QPushButton("Bağlantıyı Kes")
        self.connect_button.clicked.connect(self.start_serial_thread)
        self.disconnect_button.clicked.connect(self.stop_serial_thread)
        
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.connect_button)
        self.button_layout.addWidget(self.disconnect_button)

        # Gelen veriyi göstermek için metin alanı
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)

        self.layout.addWidget(self.port_label) # <--- DEĞİŞİKLİK: QHBoxLayout yerine QLabel eklendi
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.data_display)
        
        self.setCentralWidget(self.central_widget)

        # Başlangıçta butonları ayarla
        self.disconnect_button.setEnabled(False)

    # <--- DEĞİŞİKLİK: 'populate_ports' fonksiyonu tamamen kaldırıldı. ---
    
    def start_serial_thread(self):
        """
        Worker'ı oluşturur, QThread'e taşır ve başlatır.
        """
        # <--- DEĞİŞİKLİK: Port adı artık ComboBox'tan değil, doğrudan global değişkenden okunuyor ---
        port_name = GCS_PORT
        
        # Global BAUDRATE değişkenine erişim
        self.data_display.append(f"{port_name} portuna {BAUDRATE} baud ile bağlanılıyor...")
        
        # 1. Thread'i oluştur
        self.serial_thread = QThread()
        # 2. Worker'ı oluştur
        self.serial_worker = SerialWorker(port=port_name, baudrate=BAUDRATE)
        # 3. Worker'ı thread'e taşı
        self.serial_worker.moveToThread(self.serial_thread)

        # 4. Sinyal/Slot bağlantılarını yap
        #    Worker'dan GUI'ye (MainWindow)
        self.serial_worker.data_received.connect(self.update_data_display)
        self.serial_worker.port_error.connect(self.handle_port_error)
        
        #    Thread yaşam döngüsü
        self.serial_thread.started.connect(self.serial_worker.run) # Thread başlayınca worker'ın run() metodunu tetikle
        self.serial_worker.finished.connect(self.serial_thread.quit) # Worker işi bitince thread'i durdur
        self.serial_worker.finished.connect(self.serial_worker.deleteLater) # İş bitince worker'ı sil
        self.serial_thread.finished.connect(self.serial_thread.deleteLater) # Thread durunca sil
        self.serial_thread.finished.connect(self.on_thread_finished) # Thread bitince butonları ayarla

        # 5. Thread'i başlat
        self.serial_thread.start()

        # Buton durumlarını güncelle
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        # <--- DEĞİŞİKLİK: Kaldırılan ComboBox ve Refresh butonu ile ilgili satırlar silindi ---

    def stop_serial_thread(self):
        """
        Worker'a durma sinyali gönderir. (Thread buradan zorla kapatılmaz)
        """
        if self.serial_worker:
            self.serial_worker.stop()
            self.data_display.append("Bağlantı kesiliyor...")

    def on_thread_finished(self):
        """
        Thread güvenli bir şekilde durduğunda çağrılır.
        """
        self.data_display.append("Bağlantı kesildi.")
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        # <--- DEĞİŞİKLİK: Kaldırılan ComboBox ve Refresh butonu ile ilgili satırlar silindi ---
        # Referansları temizle
        self.serial_thread = None
        self.serial_worker = None

    def update_data_display(self, data):
        """
        Worker'dan gelen 'data_received' sinyalini yakalayan SLOT.
        Bu fonksiyon GUI thread'inde çalışır.
        """
        self.data_display.append(f"Alındı: {data}")

    def handle_port_error(self, error_msg):
        """
        Worker'dan gelen 'port_error' sinyalini yakalayan SLOT.
        """
        self.data_display.append(f"HATA: {error_msg}")
        self.stop_serial_thread() # Hata durumunda thread'i durdurmayı dene

    def closeEvent(self, event):
        """
        Ana pencere kapatıldığında thread'in de kapanmasını garanti eder.
        """
        print("Pencere kapatılıyor, thread durduruluyor...")
        self.stop_serial_thread()
        if self.serial_thread:
            # Thread'in durmasını bekle
            self.serial_thread.quit()
            self.serial_thread.wait(2000) # Max 2 saniye bekle
        event.accept()


# --- Ana Uygulama Başlangıcı ---
# GCS PORTU: com0com ile oluşturduğunuz çiftin İKİNCİ ucu
GCS_PORT = 'COM8' 
BAUDRATE = 9600

if __name__ == "__main__":
    
    # QApplication başlat
    app = QApplication(sys.argv)
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec())