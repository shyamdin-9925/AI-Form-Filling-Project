from PIL import Image
import os


def compress_file(file_path: str, max_kb: int = 10240) -> str:
    if file_path.lower().endswith('.pdf'):
        return file_path
    return compress_image(file_path, max_kb)


def compress_image(path: str, max_kb: int = 10240) -> str:
    try:
        img = Image.open(path)
        output_path = path.rsplit('.', 1)[0] + '_compressed.jpg'
        quality = 85
        img.save(output_path, optimize=True, quality=quality)
        while os.path.getsize(output_path) > max_kb * 1024 and quality > 10:
            quality -= 10
            img.save(output_path, optimize=True, quality=quality)
        return output_path
    except Exception as e:
        print(f"Compression error: {e}")
        return path