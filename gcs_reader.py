# gcs_reader.py
# Bu, pyserial, PyQt6 ve QThread kullanan Yer Kontrol İstasyonu uygulamasıdır.
# DOĞRUDAN COM8 portunu dinler.

import sys
import serial
import subprocess
import os
# import serial.tools.list_ports # <--- DEĞİŞİKLİK: Artık kullanılmıyor.
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QTextEdit, QPushButton, QLabel, QHBoxLayout, QGridLayout, QFrame
)
# 'Qt' modülü import edildi
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QCoreApplication, Qt
from PyQt6.QtGui import QFont, QPalette, QColor 

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
        self.setGeometry(100, 100, 700, 600)
        
        # Modern görünüm için stil ayarları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
            QLabel#section_title {
                font-size: 14px;
                font-weight: bold;
                color: #424242;
                padding: 5px;
            }
            QLabel#port_label {
                font-size: 13px;
                color: #616161;
                background-color: #E3F2FD;
                padding: 8px;
                border-radius: 5px;
            }
            QFrame#data_card {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
            QLabel#data_title {
                font-size: 12px;
                font-weight: bold;
                color: #757575;
                padding: 5px;
            }
            QLabel#data_value {
                font-size: 20px;
                font-weight: bold;
                color: #212121;
                padding: 5px;
            }
        """)

        # Thread ve Worker için referanslar
        self.serial_thread = None
        self.serial_worker = None
        
        # Simulatör process referansı
        self.simulator_process = None

        # Arayüz Bileşenleri
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # <--- DEĞİŞİKLİK: Port seçim alanı kaldırıldı, yerine sabit bir etiket eklendi ---
        # Port seçim alanı
        self.port_label = QLabel(f"🔌 Hedef Port: {GCS_PORT} (Sabit)")
        self.port_label.setObjectName("port_label")
        self.port_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # -----------------------------------------------------------------------------
        
        # Simulatör Kontrol Butonları
        self.sim_section = QLabel("🚀 Simulatör Kontrolü")
        self.sim_section.setObjectName("section_title")
        
        self.start_sim_button = QPushButton("▶ Simülatörü Başlat")
        self.stop_sim_button = QPushButton("⏹ Simülatörü Durdur")
        self.stop_sim_button.setStyleSheet("QPushButton { background-color: #F44336; } QPushButton:hover { background-color: #D32F2F; }")
        self.start_sim_button.clicked.connect(self.start_simulator)
        self.stop_sim_button.clicked.connect(self.stop_simulator)
        
        self.sim_button_layout = QHBoxLayout()
        self.sim_button_layout.setSpacing(10)
        self.sim_button_layout.addWidget(self.start_sim_button)
        self.sim_button_layout.addWidget(self.stop_sim_button)
        
        # Bağlantı Butonları
        self.conn_section = QLabel("📡 Bağlantı Kontrolü")
        self.conn_section.setObjectName("section_title")
        
        self.connect_button = QPushButton("🔗 Bağlan")
        self.connect_button.setStyleSheet("QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #388E3C; }")
        self.disconnect_button = QPushButton("🔌 Bağlantıyı Kes")
        self.disconnect_button.setStyleSheet("QPushButton { background-color: #FF9800; } QPushButton:hover { background-color: #F57C00; }")
        self.connect_button.clicked.connect(self.start_serial_thread)
        self.disconnect_button.clicked.connect(self.stop_serial_thread)
        
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.button_layout.addWidget(self.connect_button)
        self.button_layout.addWidget(self.disconnect_button)

        # Veri tipleri için modern kartlar (Grid Layout)
        self.data_section = QLabel("📊 Telemetri Verileri")
        self.data_section.setObjectName("section_title")
        
        self.data_grid = QGridLayout()
        self.data_grid.setSpacing(15)
        
        # Her veri tipi için kart oluştur
        self.latitude_card = self.create_data_card("📍 Enlem", "LAT")
        self.longitude_card = self.create_data_card("📍 Boylam", "LON")
        self.altitude_card = self.create_data_card("⬆️ Yükseklik", "ALT")
        self.velocity_card = self.create_data_card("🚀 Hız", "VEL")
        self.temperature_card = self.create_data_card("🌡️ Sıcaklık", "TEMP")
        self.pressure_card = self.create_data_card("🔽 Basınç", "PRES")
        self.battery_card = self.create_data_card("🔋 Batarya", "BAT")
        
        # Grid'e kartları yerleştir (3 sütun)
        self.data_grid.addWidget(self.latitude_card, 0, 0)
        self.data_grid.addWidget(self.longitude_card, 0, 1)
        self.data_grid.addWidget(self.altitude_card, 0, 2)
        self.data_grid.addWidget(self.velocity_card, 1, 0)
        self.data_grid.addWidget(self.temperature_card, 1, 1)
        self.data_grid.addWidget(self.pressure_card, 1, 2)
        self.data_grid.addWidget(self.battery_card, 2, 0, 1, 3)  # Batarya tüm genişlikte

        self.layout.addWidget(self.port_label)
        self.layout.addWidget(self.sim_section)
        self.layout.addLayout(self.sim_button_layout)
        self.layout.addWidget(self.conn_section)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.data_section)
        self.layout.addLayout(self.data_grid)
        self.layout.addStretch()
        
        self.setCentralWidget(self.central_widget)

        # Başlangıçta butonları ayarla
        self.disconnect_button.setEnabled(False)
        self.stop_sim_button.setEnabled(False)

    def create_data_card(self, title, data_type):
        """
        Modern veri kartı oluşturur.
        """
        card = QFrame()
        card.setObjectName("data_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(5)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setObjectName("data_title")
        
        # Değer
        value_label = QLabel("-")
        value_label.setObjectName("data_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        # Referansları sakla
        if data_type == "LAT":
            self.latitude_label = value_label
        elif data_type == "LON":
            self.longitude_label = value_label
        elif data_type == "ALT":
            self.altitude_label = value_label
        elif data_type == "VEL":
            self.velocity_label = value_label
        elif data_type == "TEMP":
            self.temperature_label = value_label
        elif data_type == "PRES":
            self.pressure_label = value_label
        elif data_type == "BAT":
            self.battery_label = value_label
        
        return card

    # <--- DEĞİŞİKLİK: 'populate_ports' fonksiyonu tamamen kaldırıldı. ---
    
    def start_serial_thread(self):
        """
        Worker'ı oluşturur, QThread'e taşır ve başlatır.
        """
        # <--- DEĞİŞİKLİK: Port adı artık ComboBox'tan değil, doğrudan global değişkenden okunuyor ---
        port_name = GCS_PORT
        
        # Global BAUDRATE değişkenine erişim
        print(f"{port_name} portuna {BAUDRATE} baud ile bağlanılıyor...")
        
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
            print("Bağlantı kesiliyor...")

    def on_thread_finished(self):
        """
        Thread güvenli bir şekilde durduğunda çağrılır.
        """
        print("Bağlantı kesildi.")
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
        # Veriyi parse et ve ilgili label'ı güncelle
        try:
            if ',' in data:
                parts = data.split(',')
                if len(parts) >= 2:
                    data_type = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Veri tipine göre ilgili label'ı güncelle
                    if data_type == "LAT":
                        self.latitude_label.setText(f"{value}°")
                    elif data_type == "LON":
                        self.longitude_label.setText(f"{value}°")
                    elif data_type == "ALT":
                        self.altitude_label.setText(f"{value} m")
                    elif data_type == "VEL":
                        self.velocity_label.setText(f"{value} m/s")
                    elif data_type == "TEMP":
                        self.temperature_label.setText(f"{value} °C")
                    elif data_type == "PRES":
                        self.pressure_label.setText(f"{value} hPa")
                    elif data_type == "BAT":
                        self.battery_label.setText(f"{value} V")
        except Exception as e:
            print(f"Veri parse hatası: {e}")

    def handle_port_error(self, error_msg):
        """
        Worker'dan gelen 'port_error' sinyalini yakalayan SLOT.
        """
        print(f"HATA: {error_msg}")
        self.stop_serial_thread() # Hata durumunda thread'i durdurmayı dene

    def start_simulator(self):
        """
        Simulator.py'yi yeni bir PowerShell terminalinde başlatır.
        """
        try:
            # Mevcut dizindeki simulator.py dosyasının yolunu al
            script_dir = os.path.dirname(os.path.abspath(__file__))
            simulator_path = os.path.join(script_dir, "simulator.py")
            
            # Python yorumlayıcısının yolunu al (mevcut ortamdan)
            python_exe = sys.executable
            
            # Yeni PowerShell terminalinde Python betiğini çalıştır
            # -NoExit: Terminal açık kalsın (Ctrl+C ile kapatılabilir)
            self.simulator_process = subprocess.Popen(
                ["powershell.exe", "-NoExit", "-Command", f"& '{python_exe}' '{simulator_path}'"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print("Simülatör yeni terminalde başlatıldı.")
            self.start_sim_button.setEnabled(False)
            self.stop_sim_button.setEnabled(True)
            
        except Exception as e:
            print(f"Simülatör başlatma hatası: {e}")
    
    def stop_simulator(self):
        """
        Çalışan simülatör procesini ve terminalini sonlandırır.
        """
        if self.simulator_process:
            try:
                # Process ID'yi al
                pid = self.simulator_process.pid
                
                # PowerShell komutu ile process'i ve child process'leri kapat
                # taskkill /F = Zorla kapat, /T = Alt process'leri de kapat
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    capture_output=True,
                    timeout=3
                )
                
                print("Simülatör ve terminali kapatıldı.")
            except subprocess.TimeoutExpired:
                print("Simülatör kapatma zaman aşımı.")
            except Exception as e:
                print(f"Simülatör durdurma hatası: {e}")
            finally:
                self.simulator_process = None
                self.start_sim_button.setEnabled(True)
                self.stop_sim_button.setEnabled(False)
        else:
            print("Çalışan simülatör bulunamadı.")

    def closeEvent(self, event):
        """
        Ana pencere kapatıldığında thread'in ve simülatörün de kapanmasını garanti eder.
        """
        print("Pencere kapatılıyor, thread ve simülatör durduruluyor...")
        self.stop_simulator()
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