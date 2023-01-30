from PIL import Image

def resize_image(image: str, new_width: int):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio)
    image = image.resize((new_width, new_height))
    return image