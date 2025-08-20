from PIL import Image
import os

def convert_png_to_ico():
    """Convert PNG logo to ICO format for better Windows compatibility"""
    png_path = os.path.join(os.path.dirname(__file__), "svgs", "logo.png")
    ico_path = os.path.join(os.path.dirname(__file__), "svgs", "logo.ico")
    
    if os.path.exists(png_path):
        try:
            # Open the PNG image
            img = Image.open(png_path)
            
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create multiple sizes for the ICO file (Windows prefers this)
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save(ico_path, format='ICO', sizes=sizes)
            
            print(f"Successfully converted {png_path} to {ico_path}")
            return ico_path
        except Exception as e:
            print(f"Error converting icon: {e}")
            return None
    else:
        print(f"PNG file not found: {png_path}")
        return None

if __name__ == "__main__":
    convert_png_to_ico()
