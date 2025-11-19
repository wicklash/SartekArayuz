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
        
    def start_simulator(self, project_root=None):
        """
        Simülatörü yeni bir PowerShell terminalinde başlatır.
        
        Args:
            project_root: Proje kök dizini. None ise otomatik bulunur.
        """
        if self.is_running():
            print("Simülatör zaten çalışıyor!")
            return
            
        try:
            # Proje kök dizinini bul
            if project_root is None:
                # src/core dizininden iki seviye yukarı
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
            
            simulator_path = os.path.join(project_root, self.simulator_script_name)
            
            if not os.path.exists(simulator_path):
                error_msg = f"Simülatör dosyası bulunamadı: {simulator_path}"
                print(error_msg)
                self.simulator_error.emit(error_msg)
                return
            
            # Python yorumlayıcısının yolunu al
            python_exe = sys.executable
            
            # Yeni PowerShell terminalinde Python betiğini çalıştır
            self.simulator_process = subprocess.Popen(
                ["powershell.exe", "-NoExit", "-Command", 
                 f"& '{python_exe}' '{simulator_path}'"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print(f"Simülatör başlatıldı (PID: {self.simulator_process.pid})")
            self.simulator_started.emit()
            
        except Exception as e:
            error_msg = f"Simülatör başlatma hatası: {e}"
            print(error_msg)
            self.simulator_error.emit(error_msg)
    
    def stop_simulator(self):
        """
        Çalışan simülatör process'ini ve terminalini sonlandırır.
        """
        if not self.simulator_process:
            print("Çalışan simülatör bulunamadı.")
            return
            
        try:
            pid = self.simulator_process.pid
            
            # PowerShell komutu ile process'i ve child process'leri kapat
            # taskkill /F = Zorla kapat, /T = Alt process'leri de kapat
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                timeout=3
            )
            
            print(f"Simülatör durduruldu (PID: {pid})")
            self.simulator_stopped.emit()
            
        except subprocess.TimeoutExpired:
            print("Simülatör kapatma zaman aşımı.")
            self.simulator_error.emit("Simülatör kapatma zaman aşımı")
        except Exception as e:
            error_msg = f"Simülatör durdurma hatası: {e}"
            print(error_msg)
            self.simulator_error.emit(error_msg)
        finally:
            self.simulator_process = None
    
    def is_running(self):
        """
        Simülatörün çalışıp çalışmadığını kontrol eder.
        
        Returns:
            bool: Simülatör çalışıyorsa True
        """
        if self.simulator_process is None:
            return False
            
        # Process hala çalışıyor mu kontrol et
        return self.simulator_process.poll() is None
    
    def cleanup(self):
        """
        Temizlik işlemi - uygulama kapanırken çağrılmalı.
        """
        if self.is_running():
            self.stop_simulator()
