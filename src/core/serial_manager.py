# serial_manager.py
# Thread yönetimi ve seri port bağlantı kontrolü

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from .serial_worker import SerialWorker


class SerialManager(QObject):
    """
    Seri port bağlantısını ve thread yaşam döngüsünü yönetir.
    UI'dan iş mantığını ayırır.
    """
    # UI'ye gönderilecek sinyaller
    data_received = pyqtSignal(str)     # Veri geldiğinde
    connection_error = pyqtSignal(str)  # Bağlantı hatası
    connection_started = pyqtSignal()   # Bağlantı başladı
    connection_stopped = pyqtSignal()   # Bağlantı durduruldu
    
    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_thread = None
        self.serial_worker = None
        
    def start_connection(self):
        """
        Seri port bağlantısını başlatır.
        """
        if self.serial_thread and self.serial_thread.isRunning():
            print("Bağlantı zaten aktif!")
            return
            
        print(f"{self.port} portuna {self.baudrate} baud ile bağlanılıyor...")
        
        # Thread ve Worker oluştur
        self.serial_thread = QThread()
        self.serial_worker = SerialWorker(port=self.port, baudrate=self.baudrate)
        
        # Worker'ı thread'e taşı
        self.serial_worker.moveToThread(self.serial_thread)
        
        # Sinyal bağlantıları - Worker'dan Manager'a
        self.serial_worker.data_received.connect(self._on_data_received)
        self.serial_worker.port_error.connect(self._on_port_error)
        
        # Thread yaşam döngüsü
        self.serial_thread.started.connect(self.serial_worker.run)
        self.serial_worker.finished.connect(self.serial_thread.quit)
        self.serial_worker.finished.connect(self.serial_worker.deleteLater)
        self.serial_thread.finished.connect(self.serial_thread.deleteLater)
        self.serial_thread.finished.connect(self._on_thread_finished)
        
        # Thread'i başlat
        self.serial_thread.start()
        self.connection_started.emit()
        
    def stop_connection(self):
        """
        Seri port bağlantısını durdurur.
        """
        if self.serial_worker:
            self.serial_worker.stop()
            print("Bağlantı kesiliyor...")
        else:
            print("Aktif bağlantı yok.")
            
    def is_connected(self):
        """
        Bağlantının aktif olup olmadığını kontrol eder.
        """
        return self.serial_thread is not None and self.serial_thread.isRunning()
    
    def _on_data_received(self, data):
        """
        Worker'dan gelen veriyi UI'ye iletir.
        """
        self.data_received.emit(data)
        
    def _on_port_error(self, error_msg):
        """
        Worker'dan gelen hatayı UI'ye iletir ve bağlantıyı durdurur.
        """
        print(f"Manager: Port hatası - {error_msg}")
        self.connection_error.emit(error_msg)
        self.stop_connection()
        
    def _on_thread_finished(self):
        """
        Thread durduğunda temizlik yapar.
        """
        print("Bağlantı kesildi.")
        self.serial_thread = None
        self.serial_worker = None
        self.connection_stopped.emit()
