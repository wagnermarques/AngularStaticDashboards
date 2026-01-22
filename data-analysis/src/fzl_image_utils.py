from PIL import Image
import potrace

def fzl_convert_img_raster_to_vector(image_path):
    """
    Convert a raster image to vector format using potrace.
    
    Args:
        image_path (str): Path to the input raster image.
        
    Returns:
        potrace.Path: The vector representation of the image.
    """
    # Load and convert to grayscale + threshold
    img = Image.open(image_path).convert("L")
    img = img.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize

    # Convert to bitmap for potrace
    bitmap = potrace.Bitmap(list(img.getdata()), img.width, img.height)
    path = bitmap.trace()
    
    return path



def fzl_generate_pwa_icons_from_raster_image(image_path, sizes=[48, 72, 96, 144, 192, 512]):
    """
    Generate PWA icons of specified sizes from a source image.
    
    Args:
        image_path (str): Path to the source image.
        sizes (list): List of icon sizes to generate.
        image_path (str): Path to the source image.
        sizes (list): List of icon sizes to generate.

    Returns:
        dict: A dictionary with sizes as keys and resized Image objects as values.  
    """
    img = Image.open(image_path).convert("RGBA")
    icons = {}
    
    for size in sizes:
        icon = img.resize((size, size), Image.ANTIALIAS)
        icons[size] = icon
    
    return icons
