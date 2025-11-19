# styles.py
# UI stilleri ve tema tanımlamaları

# Ana pencere ve widget stilleri
MAIN_WINDOW_STYLE = """
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
"""

# Özel buton stilleri
BUTTON_STYLES = {
    'connect': "QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #388E3C; }",
    'disconnect': "QPushButton { background-color: #FF9800; } QPushButton:hover { background-color: #F57C00; }",
    'stop': "QPushButton { background-color: #F44336; } QPushButton:hover { background-color: #D32F2F; }"
}

# Renk paleti
COLORS = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'primary_pressed': '#0D47A1',
    'success': '#4CAF50',
    'success_dark': '#388E3C',
    'warning': '#FF9800',
    'warning_dark': '#F57C00',
    'danger': '#F44336',
    'danger_dark': '#D32F2F',
    'background': '#f5f5f5',
    'card_background': 'white',
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'text_hint': '#424242',
    'border': '#E0E0E0',
    'info_background': '#E3F2FD',
    'info_text': '#616161'
}
