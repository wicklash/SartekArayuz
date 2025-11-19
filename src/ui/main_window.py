# main_window.py
# Ana arayüz sınıfı ve UI bileşenleri

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout, QGridLayout, QFrame
)
from PyQt6.QtCore import QThread, Qt
import sys
import subprocess
import os


class MainWindow(QMainWindow):
    def __init__(self, gcs_port, baudrate, worker_class):
        super().__init__()
        self.gcs_port = gcs_port
        self.baudrate = baudrate
        self.WorkerClass = worker_class
        
        self.setWindowTitle("Sartek GCS - Roket Telemetri Sistemi")
        self.setGeometry(100, 100, 1200, 800)
        
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
                font-size: 16px;
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
        
        # Port seçim alanı
        self.port_label = QLabel(f"🔌 Hedef Port: {self.gcs_port} (Sabit)")
        self.port_label.setObjectName("port_label")
        self.port_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
        self.data_grid.setSpacing(10)
        
        # 1. Kimlik ve Paket Bilgileri
        self.takim_id_card = self.create_data_card("🏷️ Takım ID", "TAKIM_ID")
        self.sayac_card = self.create_data_card("📦 Paket Sayacı", "SAYAC")
        
        # 2. Barometrik Veri
        self.irtifa_card = self.create_data_card("📏 İrtifa (Barometrik)", "IRTIFA")
        
        # 3. GPS Ana Roket
        self.roket_gps_irtifa_card = self.create_data_card("🚀 Roket GPS İrtifa", "ROKET_GPS_IRT")
        self.roket_enlem_card = self.create_data_card("🚀 Roket Enlem", "ROKET_ENLEM")
        self.roket_boylam_card = self.create_data_card("🚀 Roket Boylam", "ROKET_BOYLAM")
        
        # 4. GPS Görev Yükü
        self.gorev_gps_irtifa_card = self.create_data_card("📦 Görev Yükü GPS İrtifa", "GOREV_GPS_IRT")
        self.gorev_enlem_card = self.create_data_card("📦 Görev Yükü Enlem", "GOREV_ENLEM")
        self.gorev_boylam_card = self.create_data_card("📦 Görev Yükü Boylam", "GOREV_BOYLAM")
        
        # 5. GPS Kademe
        self.kademe_gps_irtifa_card = self.create_data_card("🔧 Kademe GPS İrtifa", "KADEME_GPS_IRT")
        self.kademe_enlem_card = self.create_data_card("🔧 Kademe Enlem", "KADEME_ENLEM")
        self.kademe_boylam_card = self.create_data_card("🔧 Kademe Boylam", "KADEME_BOYLAM")
        
        # 6. IMU Jiroskop
        self.jiroskop_x_card = self.create_data_card("🔄 Jiroskop X", "JIRO_X")
        self.jiroskop_y_card = self.create_data_card("🔄 Jiroskop Y", "JIRO_Y")
        self.jiroskop_z_card = self.create_data_card("🔄 Jiroskop Z", "JIRO_Z")
        
        # 7. IMU İvme
        self.ivme_x_card = self.create_data_card("⚡ İvme X", "IVME_X")
        self.ivme_y_card = self.create_data_card("⚡ İvme Y", "IVME_Y")
        self.ivme_z_card = self.create_data_card("⚡ İvme Z", "IVME_Z")
        
        # 8. Açı ve Durum
        self.aci_card = self.create_data_card("📐 Açı", "ACI")
        self.durum_card = self.create_data_card("🎯 Durum", "DURUM")
        self.crc_card = self.create_data_card("✅ CRC", "CRC")
        
        # Grid'e kartları yerleştir (4 sütun)
        row = 0
        # Kimlik ve Paket
        self.data_grid.addWidget(self.takim_id_card, row, 0)
        self.data_grid.addWidget(self.sayac_card, row, 1)
        self.data_grid.addWidget(self.irtifa_card, row, 2)
        self.data_grid.addWidget(self.durum_card, row, 3)
        
        row += 1
        # Ana Roket GPS
        self.data_grid.addWidget(self.roket_gps_irtifa_card, row, 0)
        self.data_grid.addWidget(self.roket_enlem_card, row, 1)
        self.data_grid.addWidget(self.roket_boylam_card, row, 2, 1, 2)
        
        row += 1
        # Görev Yükü GPS
        self.data_grid.addWidget(self.gorev_gps_irtifa_card, row, 0)
        self.data_grid.addWidget(self.gorev_enlem_card, row, 1)
        self.data_grid.addWidget(self.gorev_boylam_card, row, 2, 1, 2)
        
        row += 1
        # Kademe GPS
        self.data_grid.addWidget(self.kademe_gps_irtifa_card, row, 0)
        self.data_grid.addWidget(self.kademe_enlem_card, row, 1)
        self.data_grid.addWidget(self.kademe_boylam_card, row, 2, 1, 2)
        
        row += 1
        # IMU Jiroskop
        self.data_grid.addWidget(self.jiroskop_x_card, row, 0)
        self.data_grid.addWidget(self.jiroskop_y_card, row, 1)
        self.data_grid.addWidget(self.jiroskop_z_card, row, 2)
        self.data_grid.addWidget(self.aci_card, row, 3)
        
        row += 1
        # IMU İvme
        self.data_grid.addWidget(self.ivme_x_card, row, 0)
        self.data_grid.addWidget(self.ivme_y_card, row, 1)
        self.data_grid.addWidget(self.ivme_z_card, row, 2)
        self.data_grid.addWidget(self.crc_card, row, 3)

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
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(3)
        
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
        if data_type == "TAKIM_ID":
            self.takim_id_label = value_label
        elif data_type == "SAYAC":
            self.sayac_label = value_label
        elif data_type == "IRTIFA":
            self.irtifa_label = value_label
        elif data_type == "ROKET_GPS_IRT":
            self.roket_gps_irtifa_label = value_label
        elif data_type == "ROKET_ENLEM":
            self.roket_enlem_label = value_label
        elif data_type == "ROKET_BOYLAM":
            self.roket_boylam_label = value_label
        elif data_type == "GOREV_GPS_IRT":
            self.gorev_gps_irtifa_label = value_label
        elif data_type == "GOREV_ENLEM":
            self.gorev_enlem_label = value_label
        elif data_type == "GOREV_BOYLAM":
            self.gorev_boylam_label = value_label
        elif data_type == "KADEME_GPS_IRT":
            self.kademe_gps_irtifa_label = value_label
        elif data_type == "KADEME_ENLEM":
            self.kademe_enlem_label = value_label
        elif data_type == "KADEME_BOYLAM":
            self.kademe_boylam_label = value_label
        elif data_type == "JIRO_X":
            self.jiroskop_x_label = value_label
        elif data_type == "JIRO_Y":
            self.jiroskop_y_label = value_label
        elif data_type == "JIRO_Z":
            self.jiroskop_z_label = value_label
        elif data_type == "IVME_X":
            self.ivme_x_label = value_label
        elif data_type == "IVME_Y":
            self.ivme_y_label = value_label
        elif data_type == "IVME_Z":
            self.ivme_z_label = value_label
        elif data_type == "ACI":
            self.aci_label = value_label
        elif data_type == "DURUM":
            self.durum_label = value_label
        elif data_type == "CRC":
            self.crc_label = value_label
        
        return card

    def start_serial_thread(self):
        """
        Worker'ı oluşturur, QThread'e taşır ve başlatır.
        """
        port_name = self.gcs_port
        
        print(f"{port_name} portuna {self.baudrate} baud ile bağlanılıyor...")
        
        # 1. Thread'i oluştur
        self.serial_thread = QThread()
        # 2. Worker'ı oluştur
        self.serial_worker = self.WorkerClass(port=port_name, baudrate=self.baudrate)
        # 3. Worker'ı thread'e taşı
        self.serial_worker.moveToThread(self.serial_thread)

        # 4. Sinyal/Slot bağlantılarını yap
        #    Worker'dan GUI'ye (MainWindow)
        self.serial_worker.data_received.connect(self.update_data_display)
        self.serial_worker.port_error.connect(self.handle_port_error)
        
        #    Thread yaşam döngüsü
        self.serial_thread.started.connect(self.serial_worker.run)
        self.serial_worker.finished.connect(self.serial_thread.quit)
        self.serial_worker.finished.connect(self.serial_worker.deleteLater)
        self.serial_thread.finished.connect(self.serial_thread.deleteLater)
        self.serial_thread.finished.connect(self.on_thread_finished)

        # 5. Thread'i başlat
        self.serial_thread.start()

        # Buton durumlarını güncelle
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)

    def stop_serial_thread(self):
        """
        Worker'a durma sinyali gönderir.
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
        # Referansları temizle
        self.serial_thread = None
        self.serial_worker = None

    def update_data_display(self, data):
        """
        Worker'dan gelen 'data_received' sinyalini yakalayan SLOT.
        CSV formatında gelen veriyi parse eder.
        """
        try:
            parts = data.split(',')
            if len(parts) >= 21:  # En az 21 alan bekleniyor
                # 1. Kimlik ve Paket Bilgileri
                self.takim_id_label.setText(parts[0])
                self.sayac_label.setText(parts[1])
                
                # 2. Barometrik İrtifa
                self.irtifa_label.setText(f"{parts[2]} m")
                
                # 3. GPS Ana Roket
                self.roket_gps_irtifa_label.setText(f"{parts[3]} m")
                self.roket_enlem_label.setText(f"{parts[4]}°")
                self.roket_boylam_label.setText(f"{parts[5]}°")
                
                # 4. GPS Görev Yükü
                self.gorev_gps_irtifa_label.setText(f"{parts[6]} m")
                self.gorev_enlem_label.setText(f"{parts[7]}°")
                self.gorev_boylam_label.setText(f"{parts[8]}°")
                
                # 5. GPS Kademe
                self.kademe_gps_irtifa_label.setText(f"{parts[9]} m")
                self.kademe_enlem_label.setText(f"{parts[10]}°")
                self.kademe_boylam_label.setText(f"{parts[11]}°")
                
                # 6. IMU Jiroskop
                self.jiroskop_x_label.setText(f"{parts[12]}°/s")
                self.jiroskop_y_label.setText(f"{parts[13]}°/s")
                self.jiroskop_z_label.setText(f"{parts[14]}°/s")
                
                # 7. IMU İvme
                self.ivme_x_label.setText(f"{parts[15]} G")
                self.ivme_y_label.setText(f"{parts[16]} G")
                self.ivme_z_label.setText(f"{parts[17]} G")
                
                # 8. Açı, Durum ve CRC
                self.aci_label.setText(f"{parts[18]}°")
                
                durum_map = {
                    "0": "Beklemede",
                    "1": "Yükseliyor",
                    "2": "Tepe Noktası",
                    "3": "İniş"
                }
                durum_text = durum_map.get(parts[19], parts[19])
                self.durum_label.setText(durum_text)
                
                self.crc_label.setText(parts[20])
                
        except Exception as e:
            print(f"Veri parse hatası: {e}")
            print(f"Alınan veri: {data}")

    def handle_port_error(self, error_msg):
        """
        Worker'dan gelen 'port_error' sinyalini yakalayan SLOT.
        """
        print(f"HATA: {error_msg}")
        self.stop_serial_thread()

    def start_simulator(self):
        """
        Simulator.py'yi yeni bir PowerShell terminalinde başlatır.
        """
        try:
            # Proje kök dizinindeki simulator.py dosyasının yolunu al
            # src/ui/ dizininden iki üst seviye (proje kök dizini)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            simulator_path = os.path.join(project_root, "simulator.py")
            
            # Python yorumlayıcısının yolunu al
            python_exe = sys.executable
            
            # Yeni PowerShell terminalinde Python betiğini çalıştır
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
                pid = self.simulator_process.pid
                
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
            self.serial_thread.quit()
            self.serial_thread.wait(2000)
        event.accept()
