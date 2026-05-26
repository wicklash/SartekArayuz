# simulator_manager.py
# Simülatör process yönetimi

import sys
import subprocess
import os
from PyQt6.QtCore import QObject, pyqtSignal


class SimulatorManager(QObject):
    """
    Simülatör process'ini yönetir.
    UI'dan process yönetim mantığını ayırır.
    """
    
    # UI'ye gönderilecek sinyaller
    simulator_started = pyqtSignal()
    simulator_stopped = pyqtSignal()
    simulator_error = pyqtSignal(str)
    
    def __init__(self, simulator_script_name="simulator.py"):
        super().__init__()
        self.simulator_script_name = simulator_script_name
        self.simulator_process = None
        self.simulator_pid = None  # Başlatma anındaki PID'i sakla
        
    def start_simulator(self, project_root=None):
        """
        Simülatörü yeni bir konsol penceresinde başlatır.
        
        Args:
            project_root: Proje kök dizini. None ise otomatik bulunur.
        """
        if self.is_running():
            print("Simülatör zaten çalışıyor!")
            return
            
        try:
            # Proje kök dizinini bul
            if project_root is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
            
            python_exe = sys.executable
            is_frozen = getattr(sys, 'frozen', False)
            
            # CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP:
            # Yeni konsol penceresi açar ve bağımsız bir process group oluşturur.
            # Bu sayede taskkill /T komutu tüm alt süreçleri güvenle öldürebilir.
            creation_flags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
            
            if is_frozen:
                # EXE modunda: Ana exe ile aynı klasörde SartekSimülatör.exe aranır
                exe_dir = os.path.dirname(python_exe)
                simulator_exe_path = os.path.join(exe_dir, "SartekSimülatör.exe")
                
                if not os.path.exists(simulator_exe_path):
                    error_msg = f"Simülatör dosyası bulunamadı: {simulator_exe_path}"
                    print(error_msg)
                    self.simulator_error.emit(error_msg)
                    return
                
                self.simulator_process = subprocess.Popen(
                    [simulator_exe_path],
                    creationflags=creation_flags
                )
            else:
                # Geliştirme modunda: simulator.py çalıştırılır
                simulator_path = os.path.join(project_root, self.simulator_script_name)
                
                if not os.path.exists(simulator_path):
                    error_msg = f"Simülatör dosyası bulunamadı: {simulator_path}"
                    print(error_msg)
                    self.simulator_error.emit(error_msg)
                    return
                
                self.simulator_process = subprocess.Popen(
                    [python_exe, simulator_path],
                    creationflags=creation_flags
                )
            
            # PID'i kaydet - stop sırasında process nesnesi farklı durumda olabilir
            self.simulator_pid = self.simulator_process.pid
            print(f"Simülatör başlatıldı (PID: {self.simulator_pid})")
            self.simulator_started.emit()
            
        except Exception as e:
            error_msg = f"Simülatör başlatma hatası: {e}"
            print(error_msg)
            self.simulator_error.emit(error_msg)
    
    def stop_simulator(self):
        """
        Çalışan simülatörü ve tüm alt süreçlerini (PyInstaller inner process dahil) sonlandırır.
        taskkill /F /T kullanarak tüm process ağacını kapatır ve konsol penceresi kapanır.
        """
        if not self.simulator_pid:
            print("Çalışan simülatör bulunamadı.")
            return
            
        pid = self.simulator_pid
        print(f"Simülatör durduruluyor (PID: {pid})...")
        
        # taskkill /F /T: Zorla (/F) ve tüm alt süreçleriyle beraber (/T) kapat.
        # Bu, PyInstaller onefile EXE'nin başlattığı iç Python sürecini de kapatır
        # ve konsol penceresini anında kapatır.
        system_root = os.environ.get('SystemRoot', 'C:\\Windows')
        taskkill_path = os.path.join(system_root, 'System32', 'taskkill.exe')
        if not os.path.exists(taskkill_path):
            taskkill_path = "taskkill"
        
        try:
            result = subprocess.run(
                [taskkill_path, "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW  # taskkill penceresiz çalışsın
            )
            if result.returncode == 0:
                print(f"Simülatör başarıyla durduruldu (PID: {pid})")
                print(result.stdout.strip())
            else:
                # Process zaten kapanmış olabilir, bu normaldir
                print(f"taskkill çıktısı (kod: {result.returncode}): {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("taskkill zaman aşımı.")
        except Exception as e:
            print(f"Simülatör durdurulurken hata: {e}")
        
        # Durumu temizle ve UI'yi her halükarda güncelle
        self.simulator_process = None
        self.simulator_pid = None
        self.simulator_stopped.emit()
    
    def is_running(self):
        """
        Simülatörün çalışıp çalışmadığını kontrol eder.
        
        Returns:
            bool: Simülatör çalışıyorsa True
        """
        if self.simulator_process is None:
            return False
        return self.simulator_process.poll() is None
    
    def cleanup(self):
        """
        Temizlik işlemi - uygulama kapanırken çağrılmalı.
        """
        if self.is_running():
            self.stop_simulator()
