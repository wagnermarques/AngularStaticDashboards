from PIL import Image
import os

def fzl_generate_pwa_icons_from_raster_image(image_path, output_dir, sizes=[72, 96, 128, 144, 152, 192, 384, 512]):
    """
    Generate PWA icons of specified sizes from a source image.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    img = Image.open(image_path).convert("RGBA")
    
    for size in sizes:
        # Use Resampling.LANCZOS for newer Pillow versions
        icon = img.resize((size, size), Image.Resampling.LANCZOS)
        output_path = os.path.join(output_dir, f"icon-{size}x{size}.png")
        icon.save(output_path)
        print(f"Generated {output_path}")

def fzl_create_basic_svg(image_path, output_svg_path):
    """
    Creates a basic SVG wrapper for the image. 
    Note: Real vectorization requires potrace, but we can embed or provide 
    a placeholder if potrace is unavailable.
    """
    # For this task, we'll try to use the image dimensions
    img = Image.open(image_path)
    width, height = img.size
    
    # We'll just generate a basic SVG that could be a placeholder 
    # or a simple path if we had the vector data.
    # Since potrace is not installed, we'll notify.
    print("Vectorization (potrace) skipped. Creating basic SVG container.")
    
    svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="none"/>
  <text x="50%" y="50%" font-family="Arial" font-size="20" fill="blue" text-anchor="middle">GEPIS</text>
</svg>'''
    
    with open(output_svg_path, 'w') as f:
        f.write(svg_content)
    print(f"Basic SVG created at {output_svg_path}")

if __name__ == "__main__":
    # Absolute paths based on project structure
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOGO_PATH = "/media/wgn/btrfs400G/Projects-Srcs-GEPIS/AngularStaticDashboards/angular-app/src/imgs/gepis-logo.jpg"
    ICONS_DIR = "/media/wgn/btrfs400G/Projects-Srcs-GEPIS/AngularStaticDashboards/angular-app/public/icons"
    SVG_PATH = "/media/wgn/btrfs400G/Projects-Srcs-GEPIS/AngularStaticDashboards/angular-app/src/imgs/gepis-logo.svg"
    
    if os.path.exists(LOGO_PATH):
        fzl_generate_pwa_icons_from_raster_image(LOGO_PATH, ICONS_DIR)
        fzl_create_basic_svg(LOGO_PATH, SVG_PATH)
    else:
        print(f"Error: Source image not found at {LOGO_PATH}")