import os
from PIL import Image

img_path = 'images/UKR.png'

if os.path.exists(img_path):
    size = os.path.getsize(img_path)
    print(f"File size: {size} bytes")
    if size == 0:
        print("❌ Error: The file is empty. You need to re-download/re-save it.")
    else:
        try:
            with Image.open(img_path) as img:
                img.verify() 
                print("✅ Image is valid.")
        except Exception as e:
            print(f"❌ Image is corrupted: {e}")
else:
    print("❌ File does not exist at that path.")