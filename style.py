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
            background-color: transparent;
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
        
        /* Ensure all content inside ContentBox inherits the background */
        QWidget#ContentBox * {
            background-color: transparent;
        }
        
        /* Specific styling for content area elements */
        QWidget#ContentBox QLabel {
            background-color: transparent;
        }
        
  

        QComboBox {
            background-color: #262626; /* Keep this for contrast against the dark background */
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 6px 10px;
            color: #e5e5e5;
            font-size: 10pt;
            min-height: 16px;
            max-height: 35px;
        }

        QComboBox:hover {
            border-color: #525252;
            background-color: #2a2a2a;
        }

        QComboBox:focus {
            border-color: #db3c24;
            outline: none;
        }

        QComboBox::drop-down {
            border: none;
            width: 25px;
            background: transparent;
        }

        QComboBox::down-arrow {
            image: none;
            border: 2px solid #a3a3a3;
            width: 6px;
            height: 6px;
            border-top: none;
            border-right: none;
            transform: rotate(-45deg);
            margin-top: -3px;
        }

        QComboBox::down-arrow:hover {
            border-color: #e5e5e5;
        }

        QComboBox QAbstractItemView {
            background-color: #171717; /* Same as main app background */
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 4px;
            selection-background-color: #db3c24;
            selection-color: #ffffff;
            outline: none;
            max-height: 200px;
        }

        QComboBox QAbstractItemView::item {
            padding: 6px 10px;
            border-radius: 4px;
            margin: 1px 0;
            min-height: 16px;
            background-color: transparent;
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: #404040;
            color: #ffffff;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #db3c24;
            color: #ffffff;
        }

        QComboBox QAbstractItemView::item:disabled {
            color: #666666;
            background-color: #1f1f1f;
            font-weight: bold;
            font-size: 9pt;
            border-bottom: 1px solid #333333;
            margin: 2px 0;
            padding: 4px 8px;
        }

    """
