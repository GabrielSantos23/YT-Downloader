def dark_stylesheet() -> str:
    """
    Provides a modern, clean, dark stylesheet for the application.
    Based on the user-provided TailwindCSS dark theme.
    """
    return """
        /* --- Global --- */
        * {
            font-family: Inter, Segoe UI, Arial, sans-serif;
            color: #e5e5e5; /* --foreground */
            font-size: 10pt;
        }
        
        QMainWindow, QWidget {
            background-color: #171717; /* --background */
        }

        /* --- Labels --- */
        QLabel#TitleLabel {
            font-size: 14pt;
            font-weight: 600;
            color: #e5e5e5; /* --card-foreground */
        }
        
        QLabel#UploaderLabel {
            font-size: 10pt;
            color: #a3a3a3; /* --muted-foreground */
        }

        QLabel#MutedLabel {
            color: #a3a3a3; /* --muted-foreground */
        }

        QLabel#ThumbnailLabel {
            background-color: #262626; /* --card */
            border: 1px solid #404040; /* --border */
            border-radius: 8px;
            color: #a3a3a3; /* --muted-foreground */
        }

        /* --- Input Fields & ComboBox --- */
        QLineEdit, QComboBox {
            background-color: #262626; /* --secondary */
            border: 1px solid #404040; /* --input */
            border-radius: 6px;
            padding: 8px;
            color: #e5e5e5; /* --secondary-foreground */
        }
        QLineEdit:focus, QComboBox:focus {
            border-color: #f59e0b; /* --ring */
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            /* A proper icon should be used here */
            /* For now, it will use the system default arrow */
        }
        
        QComboBox QAbstractItemView {
            background-color: #262626; /* --popover */
            border: 1px solid #404040; /* --border */
            selection-background-color: #5b0d0b; /* --accent */
            selection-color: #fde68a; /* --accent-foreground */
        }

        /* --- Buttons --- */
        QPushButton {
            background-color: #262626; /* --secondary */
            border: 1px solid #404040; /* --border */
            padding: 8px 16px;
            border-radius: 6px;
            color: #e5e5e5; /* --secondary-foreground */
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #404040; /* A slightly lighter shade for hover */
        }
        QPushButton:pressed {
            background-color: #171717; /* --background */
        }
        QPushButton:disabled {
            background-color: #262626;
            color: #a3a3a3; /* --muted-foreground */
        }

        /* Accent button for primary actions */
        QPushButton#AccentButton {
            background-color: #db3c24; /* --primary */
            color: #000000; /* --primary-foreground */
            border: none;
        }
        QPushButton#AccentButton:hover {
            /* Creating a slightly lighter version for hover */
            background-color: #e74c3c; 
        }
        QPushButton#AccentButton:pressed {
            /* Creating a slightly darker version for pressed */
            background-color: #c0392b; 
        }
        QPushButton#AccentButton:disabled {
            background-color: #262626;
            color: #a3a3a3;
        }

        /* --- Progress Bar --- */
        QProgressBar {
            border: 1px solid #404040; /* --border */
            border-radius: 5px;
            text-align: center;
            background-color: #262626; /* --muted */
        }
        QProgressBar::chunk {
            background-color: #db3c24; /* --primary */
            border-radius: 4px;
        }
        
        /* --- Menu --- */
        QMenu {
            background-color: #262626; /* --popover */
            border: 1px solid #404040; /* --border */
            padding: 5px;
        }
        QMenu::item {
            padding: 8px 20px;
            border-radius: 4px;
            color: #e5e5e5; /* --popover-foreground */
        }
        QMenu::item:selected {
            background-color: #5b0d0b; /* --accent */
            color: #fde68a; /* --accent-foreground */
        }
        QMenu::separator {
            height: 1px;
            background: #404040; /* --border */
            margin: 5px 0;
        }

        /* --- Other Widgets --- */
        QWidget#ContentBox {
            background-color: #262626; /* --card */
            border-radius: 8px;
        }
    """
