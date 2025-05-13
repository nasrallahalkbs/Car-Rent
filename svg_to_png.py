import os
import cairosvg
import io
from PIL import Image

# القائمة بملفات SVG التي نريد تحويلها
svg_files = ['front.svg', 'rear.svg', 'side.svg', 'side2.svg', 'top.svg']

# المجلد الذي يحتوي على الملفات
source_dir = 'static/car_images'
target_dir = 'static/car_images'

# إنشاء PNG من كل ملف SVG
for svg_file in svg_files:
    svg_path = os.path.join(source_dir, svg_file)
    png_filename = os.path.splitext(svg_file)[0] + '.png'
    png_path = os.path.join(target_dir, png_filename)
    
    print(f"تحويل {svg_file} إلى {png_filename}...")
    
    # قراءة ملف SVG
    with open(svg_path, 'rb') as f:
        svg_data = f.read()
    
    # تحويل SVG إلى PNG باستخدام cairosvg
    png_data = cairosvg.svg2png(bytestring=svg_data, scale=2.0)
    
    # حفظ الصورة باستخدام pillow
    img = Image.open(io.BytesIO(png_data))
    img.save(png_path)
    
    print(f"تم حفظ {png_path}")

print("تم تحويل جميع الملفات بنجاح!")