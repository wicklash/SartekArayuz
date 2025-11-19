# port_info_widget.py
# Port bilgi gösterimi widget'ı

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class PortInfoWidget(QLabel):
    """
    Port bilgilerini gösteren widget.
    """
    
    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'yi yapılandırır."""
        self.setText(f"🔌 Hedef Port: {self.port_name} (Sabit)")
        self.setObjectName("port_label")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def update_port(self, new_port):
        """Port adını günceller."""
        self.port_name = new_port
        self.setText(f"🔌 Hedef Port: {self.port_name} (Sabit)")
