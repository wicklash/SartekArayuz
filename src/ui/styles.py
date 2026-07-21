# styles.py
# UI stilleri ve tema tanımlamaları

# Ana pencere ve widget stilleri
MAIN_WINDOW_STYLE = """
    QMainWindow {
        background-color: #1a1a1a;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    QPushButton {
        background-color: #3d3d3d;
        color: #e0e0e0;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        min-width: 70px;
        letter-spacing: 0.3px;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    QPushButton:hover {
        background-color: #4d4d4d;
    }
    QPushButton:pressed {
        background-color: #2d2d2d;
    }
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666666;
    }
    QLabel#section_title {
        font-size: 15px;
        font-weight: 600;
        color: #e0e0e0;
        padding: 8px 0px;
        letter-spacing: 0.3px;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    QLabel#port_label {
        font-size: 13px;
        color: #e0e0e0;
        background-color: #2d2d2d;
        padding: 10px 15px;
        border-radius: 4px;
        border: 1px solid #3d3d3d;
        font-weight: 500;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    QFrame#data_card {
        background-color: #2d2d2d;
        border-radius: 6px;
        border: 1px solid #3d3d3d;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    QLabel#data_title {
        font-size: 12px;
        font-weight: 700;
        color: #00d2ff;
        padding-bottom: 4px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    QLabel#data_value {
        font-size: 20px;
        font-weight: 600;
        color: #00ff00;
        padding: 2px;
        line-height: 1.3;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
    QLabel#single_data_value {
        font-size: 26px;
        font-weight: 700;
        color: #00ff00;
        padding-top: 12px;
        font-family: 'Aptos Display', 'Segoe UI', sans-serif;
    }
"""

# Özel buton stilleri
BUTTON_STYLES = {
    'start': """
        QPushButton { 
            background-color: #4caf50; 
            color: white; 
        } 
        QPushButton:hover { 
            background-color: #66bb6a; 
        } 
        QPushButton:pressed { 
            background-color: #81c784; 
        }
        QPushButton:disabled {
            background-color: #2d5f2f;
            color: #a0a0a0;
        }
    """,
    'stop': """
        QPushButton { 
            background-color: #f44336; 
            color: white; 
        } 
        QPushButton:hover { 
            background-color: #ef5350; 
        } 
        QPushButton:pressed { 
            background-color: #e57373; 
        }
        QPushButton:disabled {
            background-color: #6d2923;
            color: #a0a0a0;
        }
    """,
    'connect': """
        QPushButton { 
            background-color: #4caf50; 
            color: white; 
        } 
        QPushButton:hover { 
            background-color: #66bb6a; 
        } 
        QPushButton:pressed { 
            background-color: #81c784; 
        }
        QPushButton:disabled {
            background-color: #2d5f2f;
            color: #a0a0a0;
        }
    """,
    'disconnect': """
        QPushButton { 
            background-color: #f44336; 
            color: white; 
        } 
        QPushButton:hover { 
            background-color: #ef5350; 
        } 
        QPushButton:pressed { 
            background-color: #e57373; 
        }
        QPushButton:disabled {
            background-color: #6d2923;
            color: #a0a0a0;
        }
    """
}

# Renk paleti
COLORS = {
    'primary': '#1a1a1a',
    'secondary': '#2d2d2d',
    'tertiary': '#3d3d3d',
    'hover': '#4d4d4d',
    'accent_green': '#4caf50',
    'accent_green_light': '#66bb6a',
    'accent_green_dark': '#388e3c',
    'accent_red': '#f44336',
    'accent_red_light': '#ef5350',
    'accent_red_dark': '#d32f2f',
    'value_green': '#00ff00',
    'text_primary': '#e0e0e0',
    'text_secondary': '#999999',
    'text_disabled': '#666666',
    'border': '#3d3d3d',
    'background_dark': '#1a1a1a',
    'surface': '#2d2d2d'
}

# Log Penceresi Stilleri
DATA_LOG_WINDOW_STYLE = """
    QMainWindow {
        background-color: #1a1a1a;
    }
"""

TABLE_VIEW_STYLE = """
    QTableView {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        gridline-color: #3d3d3d;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 11px;
        selection-background-color: #4d4d4d;
    }
    QHeaderView::section {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 8px;
        border: 1px solid #3d3d3d;
        font-weight: 700;
        font-size: 10px;
        text-transform: uppercase;
    }
"""

CLEAR_BUTTON_STYLE = """
    QPushButton {
        background-color: #f44336;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #ef5350;
    }
"""
