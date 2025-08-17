from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QTransform
from PySide6.QtWidgets import QPushButton, QLabel
import os

# Try to import SVG support, fallback gracefully if not available
try:
    from PySide6.QtSvgWidgets import QSvgWidget
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False


class LoadingButton(QPushButton):
    """A button that shows loading state with the spinning SVG inside."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.text = text
        self.is_loading = False
        self.rotation_angle = 0
        self.setup_loading_widget()
        self.setup_animation()
        
    def setup_loading_widget(self):
        """Setup the loading widget."""
        # Create loading widget as a child of the button
        if SVG_AVAILABLE:
            self.loading_widget = QSvgWidget(self)
            self.loading_widget.setFixedSize(16, 16)
            self.load_svg()
        else:
            self.loading_widget = QLabel(self)
            self.loading_widget.setFixedSize(16, 16)
            self.create_fallback_loading()
        
        self.loading_widget.hide()
        
    def load_svg(self):
        """Load the SVG and apply the app's color scheme."""
        if not SVG_AVAILABLE:
            self.create_fallback_loading()
            return
            
        svg_path = os.path.join(os.path.dirname(__file__), "svgs", "loading_line.svg")
        
        if os.path.exists(svg_path):
            try:
                with open(svg_path, 'r') as f:
                    svg_content = f.read()
                
                # Replace the colors in the SVG to match the app theme
                svg_content = svg_content.replace('#09244B', '#db3c24')  # Primary color
                svg_content = svg_content.replace('stop-opacity=\'.55\'', 'stop-opacity=\'0.8\'')
                
                # Create a temporary file with the modified SVG
                temp_svg_path = os.path.join(os.path.dirname(__file__), "temp_loading.svg")
                with open(temp_svg_path, 'w') as f:
                    f.write(svg_content)
                
                self.loading_widget.load(temp_svg_path)
                
                # Clean up temp file
                try:
                    os.remove(temp_svg_path)
                except:
                    pass
            except Exception as e:
                print(f"Error loading SVG: {e}")
                self.create_fallback_loading()
        else:
            self.create_fallback_loading()
    
    def create_fallback_loading(self):
        """Create a fallback loading indicator if SVG is not available."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a simple spinning circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#db3c24"))
        painter.drawEllipse(1, 1, 14, 14)
        
        painter.end()
        
        if hasattr(self.loading_widget, 'setPixmap'):
            self.loading_widget.setPixmap(pixmap)
    
    def setup_animation(self):
        """Setup the spinning animation using a timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
    def rotate(self):
        """Rotate the loading widget."""
        self.rotation_angle = (self.rotation_angle + 15) % 360
        
        # Apply rotation transform
        transform = QTransform()
        transform.translate(8, 8)  # Center of the 16x16 widget
        transform.rotate(self.rotation_angle)
        transform.translate(-8, -8)
        
        # Check if the widget supports setTransform
        if hasattr(self.loading_widget, 'setTransform'):
            self.loading_widget.setTransform(transform)
        else:
            # For SVG widgets, we need to recreate the widget with rotation
            self.recreate_svg_with_rotation()
    
    def recreate_svg_with_rotation(self):
        """Recreate the SVG widget with rotation applied."""
        if not SVG_AVAILABLE or not hasattr(self.loading_widget, 'load'):
            return
            
        svg_path = os.path.join(os.path.dirname(__file__), "svgs", "loading_line.svg")
        
        if os.path.exists(svg_path):
            try:
                with open(svg_path, 'r') as f:
                    svg_content = f.read()
                
                # Replace the colors in the SVG to match the app theme
                svg_content = svg_content.replace('#09244B', '#db3c24')  # Primary color
                svg_content = svg_content.replace('stop-opacity=\'.55\'', 'stop-opacity=\'0.8\'')
                
                # Add rotation transform to the SVG
                # Find the root <svg> tag and add transform
                if '<svg' in svg_content and 'transform=' not in svg_content:
                    # Insert transform attribute into the svg tag
                    svg_content = svg_content.replace(
                        '<svg',
                        f'<svg transform="rotate({self.rotation_angle} 8 8)"'
                    )
                
                # Create a temporary file with the modified SVG
                temp_svg_path = os.path.join(os.path.dirname(__file__), "temp_loading.svg")
                with open(temp_svg_path, 'w') as f:
                    f.write(svg_content)
                
                self.loading_widget.load(temp_svg_path)
                
                # Clean up temp file
                try:
                    os.remove(temp_svg_path)
                except:
                    pass
            except Exception as e:
                print(f"Error rotating SVG: {e}")
    
    def setLoading(self, loading: bool):
        """Set the loading state."""
        self.is_loading = loading
        
        if loading:
            self.setText("")
            self.loading_widget.show()
            self.timer.start(50)  # Update every 50ms for smooth rotation
            self.setEnabled(False)
        else:
            self.setText(self.text)
            self.timer.stop()
            self.loading_widget.hide()
            # Reset rotation
            if hasattr(self.loading_widget, 'setTransform'):
                self.loading_widget.setTransform(QTransform())
            else:
                # Reload the original SVG without rotation
                self.load_svg()
            self.rotation_angle = 0
            self.setEnabled(True)
    
    def setText(self, text):
        """Set the button text."""
        self.text = text
        if not self.is_loading:
            super().setText(text)
    
    def resizeEvent(self, event):
        """Handle resize events to position the loading widget."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_widget'):
            # Center the loading widget in the button
            x = (self.width() - self.loading_widget.width()) // 2
            y = (self.height() - self.loading_widget.height()) // 2
            self.loading_widget.move(x, y)
