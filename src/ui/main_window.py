# main_window.py
# Ana arayüz sınıfı ve UI bileşenleri

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen, QIcon
from .styles import MAIN_WINDOW_STYLE, BUTTON_STYLES
from ..core.serial_manager import SerialManager
from ..core.data_parser import DataParser
from ..core.simulator_manager import SimulatorManager
from ..core.transmitter_manager import TransmitterManager
from ..core.csv_logger import CSVLogger
from ..core import config  # Config modülü eklendi
from .widgets.port_info_widget import PortInfoWidget
from .widgets.simulator_control_widget import SimulatorControlWidget
from .widgets.connection_control_widget import ConnectionControlWidget
from .widgets.telemetry_grid_widget import TelemetryGridWidget
from .widgets.altitude_chart_widget import AltitudeChartWidget
from .widgets.data_log_widget import DataLogWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.baudrate satırı silindi, artık config'den alınıyor
        self.selected_port = None  # UI'den seçilecek port
        
        self.setWindowTitle("Sartek GCS - Roket Telemetri Sistemi")
        self.setWindowIcon(QIcon(config.get_resource_path("assets/icon.ico")))
        self.resize(1300, 920)
        self.setMinimumSize(1100, 800)  # Minimum boyut ayarı
        
        # Pencereyi ekranın ortasına yerleştir
        screen = QScreen.availableGeometry(self.screen())
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Modern görünüm için stil ayarları
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        # Config değerleri
        receiver_baudrate = config.RECEIVER_BAUDRATE
        transmitter_baudrate = config.TRANSMITTER_BAUDRATE

        # Serial Manager oluştur (port başlangıçta None, UI'den seçilecek)
        self.serial_manager = SerialManager(port=None, baudrate=receiver_baudrate)
        
        # Manager sinyallerini bağla
        self.serial_manager.data_received.connect(self.on_data_received)
        self.serial_manager.connection_error.connect(self.handle_connection_error)
        self.serial_manager.connection_started.connect(self.on_connection_started)
        self.serial_manager.connection_stopped.connect(self.on_connection_stopped)
        
        # Transmitter Manager oluştur (hakem arayüzüne veri göndermek için)
        self.transmitter_manager = TransmitterManager(None, transmitter_baudrate)
        
        # Transmitter sinyallerini bağla
        self.transmitter_manager.transmission_error.connect(self.handle_transmission_error)
        self.transmitter_manager.transmission_started.connect(self.on_transmission_started)
        self.transmitter_manager.transmission_stopped.connect(self.on_transmission_stopped)
        
        # Simulator Manager oluştur
        self.simulator_manager = SimulatorManager()
        
        # CSV Logger oluştur
        self.csv_logger = CSVLogger()
        
        # Simulator sinyallerini bağla
        self.simulator_manager.simulator_started.connect(self.on_simulator_started)
        self.simulator_manager.simulator_stopped.connect(self.on_simulator_stopped)
        self.simulator_manager.simulator_error.connect(self.on_simulator_error)

        # Arayüz Bileşenleri
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Port bilgi widget'ı (port seçimi burada yapılır)
        # Alıcı Port: GCS için, Verici Port: Hakem arayüzüne veri göndermek için
        self.port_info_widget = PortInfoWidget("Port seçilmedi", "Port seçilmedi")
        self.port_info_widget.receiver_port_selected.connect(self._on_receiver_port_selected)
        self.port_info_widget.transmitter_port_selected.connect(self._on_transmitter_port_selected)
        
        # Ana horizontal layout (Sol: Kontrol, Sağ: Container)
        main_horizontal_layout = QHBoxLayout()
        
        # Sol panel: Kontrol menüsü (%30)
        control_panel = QFrame()
        control_panel.setObjectName("control_container")
        control_panel.setMaximumWidth(400)
        control_panel.setStyleSheet("""
            QFrame#control_container {
                background-color: #2d2d2d;
                border-radius: 6px;
                border: 1px solid #3d3d3d;
            }
        """)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(10, 10, 10, 10)
        
        # Kontrol başlığı
        control_title = QLabel("Kontrol")
        control_title.setObjectName("section_title")
        control_layout.addWidget(control_title)
        
        # Simülatör kontrol widget'ı
        self.simulator_control_widget = SimulatorControlWidget(BUTTON_STYLES)
        self.simulator_control_widget.start_requested.connect(self.start_simulator)
        self.simulator_control_widget.stop_requested.connect(self.stop_simulator)
        
        # Alıcı Port Bağlantı Kontrolü
        receiver_label = QLabel("📥 Alıcı Port Bağlantısı")
        receiver_label.setStyleSheet("color: #e0e0e0; font-size: 11px; font-weight: bold;")
        
        self.receiver_connection_widget = ConnectionControlWidget(BUTTON_STYLES)
        self.receiver_connection_widget.connect_requested.connect(self.start_serial_connection)
        self.receiver_connection_widget.disconnect_requested.connect(self.stop_serial_connection)
        
        # Verici Port Bağlantı Kontrolü
        transmitter_label = QLabel("📤 Verici Port Bağlantısı")
        transmitter_label.setStyleSheet("color: #e0e0e0; font-size: 11px; font-weight: bold;")
        
        self.transmitter_connection_widget = ConnectionControlWidget(BUTTON_STYLES)
        self.transmitter_connection_widget.connect_requested.connect(self.start_transmitter_connection)
        self.transmitter_connection_widget.disconnect_requested.connect(self.stop_transmitter_connection)
        
        control_layout.addWidget(self.simulator_control_widget)
        control_layout.addWidget(receiver_label)
        control_layout.addWidget(self.receiver_connection_widget)
        control_layout.addWidget(transmitter_label)
        control_layout.addWidget(self.transmitter_connection_widget)
        control_layout.addStretch()
        
        # Sağ panel: Boş container (%70)
        right_container = QFrame()
        right_container.setObjectName("right_container")
        right_container.setStyleSheet("""
            QFrame#right_container {
                background-color: #2d2d2d;
                border-radius: 6px;
                border: 1px solid #3d3d3d;
            }
        """)
        # Sağ panel: İrtifa grafiği
        self.altitude_chart = AltitudeChartWidget()
        
        right_container_layout = QVBoxLayout(right_container)
        right_container_layout.setContentsMargins(10, 10, 10, 10)
        right_container_layout.addWidget(self.altitude_chart)
        
        # Horizontal layout'a ekle
        main_horizontal_layout.addWidget(control_panel, 30)
        main_horizontal_layout.addWidget(right_container, 70)

        # Telemetri grid widget'ı
        self.telemetry_grid_widget = TelemetryGridWidget()
        
        # Data log widget'ı
        self.data_log_widget = DataLogWidget()
        
        # Widget'ları layout'a ekle
        self.layout.addWidget(self.port_info_widget)
        self.layout.addLayout(main_horizontal_layout, 2)  # Grafik satırı
        self.layout.addWidget(self.telemetry_grid_widget, 0)  # Telemetri kartları
        self.layout.addWidget(self.data_log_widget, 0)  # Data log
        
        self.setCentralWidget(self.central_widget)

    def _on_receiver_port_selected(self, port):
        """
        Alıcı port seçildiğinde çağrılır.
        
        Args:
            port: Seçilen alıcı port adı
        """
        self.selected_port = port
        print(f"Alıcı port seçildi: {port}")
    
    def _on_transmitter_port_selected(self, port):
        """
        Verici port seçildiğinde çağrılır.
        Artık otomatik bağlanmaz, kullanıcı manuel olarak bağlanmalı.
        
        Args:
            port: Seçilen verici port adı
        """
        print(f"Verici port seçildi: {port}")
        self.transmitter_manager.set_port(port)
    
    def start_serial_connection(self):
        """
        Seri port bağlantısını başlatır (Manager üzerinden).
        Port bilgisi port_info_widget'ten alınır.
        """
        port = self.port_info_widget.get_selected_port()
        if not port:
            print("Lütfen geçerli bir port seçin.")
            return
        
        self.selected_port = port
        self.serial_manager.set_port(port)
        self.serial_manager.start_connection()

    def stop_serial_connection(self):
        """
        Seri port bağlantısını durdurur (Manager üzerinden).
        """
        self.serial_manager.stop_connection()
    
    def start_transmitter_connection(self):
        """
        Verici port bağlantısını başlatır.
        Port bilgisi port_info_widget'ten alınır.
        """
        port = self.port_info_widget.get_transmitter_port()
        if not port:
            print("Lütfen geçerli bir verici port seçin.")
            return
        
        self.transmitter_manager.set_port(port)
        self.transmitter_manager.start_transmission()
    
    def stop_transmitter_connection(self):
        """
        Verici port bağlantısını durdurur.
        """
        self.transmitter_manager.stop_transmission()
    
    def on_connection_started(self):
        """
        Alıcı port bağlantı başladığında UI'yi günceller.
        """
        self.receiver_connection_widget.set_connected(True)
        self.port_info_widget.set_receiver_port_enabled(False)  # Bağlıyken alıcı port seçimini devre dışı bırak
        print("UI: Bağlantı kuruldu.")
        
        # Loglamayı başlat
        self.csv_logger.start_logging()
    
    def on_connection_stopped(self):
        """
        Alıcı port bağlantı durdurulduğunda UI'yi günceller.
        """
        self.receiver_connection_widget.set_connected(False)
        self.port_info_widget.set_receiver_port_enabled(True)  # Alıcı port seçimini tekrar etkinleştir
        print("UI: Bağlantı kesildi.")
        
        # Loglamayı durdur
        self.csv_logger.stop_logging()

    def on_data_received(self, raw_data):
        """
        Manager'dan gelen ham veriyi parse eder ve UI'yi günceller.
        Aynı zamanda hakem arayüzüne gönderir.
        
        Args:
            raw_data: Binary formatında ham veri (78 byte paket)
        """
        # Hakem arayüzüne gönder (aynı binary format, parse edilmeden)
        if self.transmitter_manager.is_transmitting():
            self.transmitter_manager.send_data(raw_data)
        
        # DataParser ile parse et
        telemetry = DataParser.parse(raw_data)
        
        if telemetry is None:
            return  # Parse hatası (Header / Footer / Boyut)
        
        # Checksum durumunu üst panelde göster
        self.port_info_widget.update_checksum_status(
            telemetry.checksum_error, 
            telemetry.checksum_calculated, 
            telemetry.checksum
        )
        
        # Parse edilmiş veriyi log widget'a ekle (binary hex yerine parse edilmiş veri)
        self.data_log_widget.add_log(telemetry)
        
        # CSV dosyasına kaydet
        self.csv_logger.log(telemetry)
        
        # UI'yi güncelle
        self.telemetry_grid_widget.update_data(telemetry)
        
        # İrtifa grafiğine veri ekle (direkt float değer - performans için)
        self.altitude_chart.add_altitude(telemetry.irtifa)
        
        # Detay penceresine veri ekle (pencere açık olmasa bile buffer'a eklenir)
        self.data_log_widget.detail_window.add_log_entry(telemetry)

    def handle_connection_error(self, error_msg):
        """
        Manager'dan gelen bağlantı hatasını işler.
        """
        print(f"UI HATA: {error_msg}")
        # Opsiyonel: Kullanıcıya hata mesajı gösterilebilir (QMessageBox)
    
    def handle_transmission_error(self, error_msg):
        """
        TransmitterManager'dan gelen hataları işler.
        """
        print(f"UI VERİCİ HATA: {error_msg}")
        # Opsiyonel: Kullanıcıya hata mesajı gösterilebilir (QMessageBox)
    
    def on_transmission_started(self):
        """
        Verici bağlantı başladığında çağrılır.
        """
        self.transmitter_connection_widget.set_connected(True)
        self.port_info_widget.set_transmitter_port_enabled(False)  # Bağlıyken verici port seçimini devre dışı bırak
        print("UI: Verici bağlantı kuruldu.")
    
    def on_transmission_stopped(self):
        """
        Verici bağlantı durdurulduğunda çağrılır.
        """
        self.transmitter_connection_widget.set_connected(False)
        self.port_info_widget.set_transmitter_port_enabled(True)  # Verici port seçimini tekrar etkinleştir
        print("UI: Verici bağlantı kesildi.")

    def start_simulator(self):
        """
        Simülatörü başlatır (Manager üzerinden).
        """
        self.simulator_manager.start_simulator()
    
    def stop_simulator(self):
        """
        Simülatörü durdurur (Manager üzerinden).
        """
        self.simulator_manager.stop_simulator()
    
    def on_simulator_started(self):
        """
        Simülatör başladığında UI'yi günceller.
        """
        self.simulator_control_widget.set_simulator_running(True)
        print("UI: Simülatör başlatıldı.")
        
        # Loglamayı başlat
        self.csv_logger.start_logging()
    
    def on_simulator_stopped(self):
        """
        Simülatör durdurulduğunda UI'yi günceller.
        """
        self.simulator_control_widget.set_simulator_running(False)
        print("UI: Simülatör durduruldu.")
        
        # Loglamayı durdur
        self.csv_logger.stop_logging()
    
    def on_simulator_error(self, error_msg):
        """
        Simülatör hatasını işler.
        """
        print(f"UI Simülatör Hatası: {error_msg}")
        # Opsiyonel: QMessageBox ile kullanıcıya göster

    def closeEvent(self, event):
        """
        Ana pencere kapatıldığında bağlantı ve simülatörü durdurur.
        """
        print("Pencere kapatılıyor, bağlantı ve simülatör durduruluyor...")
        
        # Simülatör ve serial bağlantıyı temizle
        self.simulator_manager.cleanup()
        self.serial_manager.stop_connection()
        self.transmitter_manager.stop_transmission()
        self.csv_logger.stop_logging()
        
        # Manager'ların thread'lerini bekle
        if self.serial_manager.serial_thread:
            self.serial_manager.serial_thread.quit()
            self.serial_manager.serial_thread.wait(2000)
        
        if self.transmitter_manager.transmitter_thread:
            self.transmitter_manager.transmitter_thread.quit()
            self.transmitter_manager.transmitter_thread.wait(2000)
        
        event.accept()
