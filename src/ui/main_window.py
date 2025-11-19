# main_window.py
# Ana arayüz sınıfı ve UI bileşenleri

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from .styles import MAIN_WINDOW_STYLE, BUTTON_STYLES
from ..core.serial_manager import SerialManager
from ..core.data_parser import DataParser
from ..core.simulator_manager import SimulatorManager
from .widgets.port_info_widget import PortInfoWidget
from .widgets.simulator_control_widget import SimulatorControlWidget
from .widgets.connection_control_widget import ConnectionControlWidget
from .widgets.telemetry_grid_widget import TelemetryGridWidget


class MainWindow(QMainWindow):
    def __init__(self, gcs_port, baudrate, worker_class):
        super().__init__()
        self.gcs_port = gcs_port
        self.baudrate = baudrate
        
        self.setWindowTitle("Sartek GCS - Roket Telemetri Sistemi")
        self.setGeometry(100, 100, 1200, 800)
        
        # Modern görünüm için stil ayarları
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        # Serial Manager oluştur
        self.serial_manager = SerialManager(gcs_port, baudrate)
        
        # Manager sinyallerini bağla
        self.serial_manager.data_received.connect(self.on_data_received)
        self.serial_manager.connection_error.connect(self.handle_connection_error)
        self.serial_manager.connection_started.connect(self.on_connection_started)
        self.serial_manager.connection_stopped.connect(self.on_connection_stopped)
        
        # Simulator Manager oluştur
        self.simulator_manager = SimulatorManager()
        
        # Simulator sinyallerini bağla
        self.simulator_manager.simulator_started.connect(self.on_simulator_started)
        self.simulator_manager.simulator_stopped.connect(self.on_simulator_stopped)
        self.simulator_manager.simulator_error.connect(self.on_simulator_error)

        # Arayüz Bileşenleri
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Port bilgi widget'ı
        self.port_info_widget = PortInfoWidget(f"{self.gcs_port} (Sabit)")
        
        # Simulatör kontrol widget'ı
        self.simulator_control_widget = SimulatorControlWidget(BUTTON_STYLES)
        self.simulator_control_widget.start_requested.connect(self.start_simulator)
        self.simulator_control_widget.stop_requested.connect(self.stop_simulator)
        
        # Bağlantı kontrol widget'ı
        self.connection_control_widget = ConnectionControlWidget(BUTTON_STYLES)
        self.connection_control_widget.connect_requested.connect(self.start_serial_connection)
        self.connection_control_widget.disconnect_requested.connect(self.stop_serial_connection)

        # Telemetri grid widget'ı
        self.telemetry_grid_widget = TelemetryGridWidget()
        
        # Widget'ları layout'a ekle
        self.layout.addWidget(self.port_info_widget)
        self.layout.addWidget(self.simulator_control_widget)
        self.layout.addWidget(self.connection_control_widget)
        self.layout.addWidget(self.telemetry_grid_widget)
        self.layout.addStretch()
        
        self.setCentralWidget(self.central_widget)

    def start_serial_connection(self):
        """
        Seri port bağlantısını başlatır (Manager üzerinden).
        """
        self.serial_manager.start_connection()

    def stop_serial_connection(self):
        """
        Seri port bağlantısını durdurur (Manager üzerinden).
        """
        self.serial_manager.stop_connection()
    
    def on_connection_started(self):
        """
        Bağlantı başladığında UI'yi günceller.
        """
        self.connection_control_widget.set_connected(True)
        print("UI: Bağlantı kuruldu.")
    
    def on_connection_stopped(self):
        """
        Bağlantı durdurulduğunda UI'yi günceller.
        """
        self.connection_control_widget.set_connected(False)
        print("UI: Bağlantı kesildi.")

    def on_data_received(self, raw_data):
        """
        Manager'dan gelen ham veriyi parse eder ve UI'yi günceller.
        """
        # DataParser ile parse et
        telemetry = DataParser.parse(raw_data)
        
        if telemetry is None:
            return  # Parse hatası
        
        # UI'yi güncelle
        self.telemetry_grid_widget.update_data(telemetry)

    def handle_connection_error(self, error_msg):
        """
        Manager'dan gelen bağlantı hatasını işler.
        """
        print(f"UI HATA: {error_msg}")
        # Opsiyonel: Kullanıcıya hata mesajı gösterilebilir (QMessageBox)

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
    
    def on_simulator_stopped(self):
        """
        Simülatör durdurulduğunda UI'yi günceller.
        """
        self.simulator_control_widget.set_simulator_running(False)
        print("UI: Simülatör durduruldu.")
    
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
        
        # Manager'ın thread'ini bekle
        if self.serial_manager.serial_thread:
            self.serial_manager.serial_thread.quit()
            self.serial_manager.serial_thread.wait(2000)
        
        event.accept()
