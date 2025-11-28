import requests
import os
import glob
from PIL import Image, ImageDraw, ImageFont

# CONFIGURATION
API_URL = "http://localhost:8000/detect"
INPUT_FOLDER = "test_images"   # The folder with your 4 subfolders
OUTPUT_FOLDER = "results"      # Where we will save the annotated images

def draw_boxes(image_path, traffic_signs, objects, output_path):
    """Draws bounding boxes and labels on the image"""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Draw Traffic Signs (Red Boxes)
        for sign in traffic_signs:
            box = sign['box']
            label = f"{sign['label']} ({sign['confidence']})"
            draw.rectangle(box, outline="red", width=3)
            # Draw text background
            draw.rectangle([box[0], box[1]-20, box[0]+150, box[1]], fill="red")
            draw.text((box[0]+5, box[1]-15), label, fill="white")

        # Draw Objects like Cars/People (Blue Boxes)
        for obj in objects:
            box = obj['box']
            label = f"{obj['label']} ({obj['confidence']})"
            draw.rectangle(box, outline="blue", width=3)
            draw.rectangle([box[0], box[1]-20, box[0]+150, box[1]], fill="blue")
            draw.text((box[0]+5, box[1]-15), label, fill="white")

        # Save result
        img.save(output_path)
        print(f"   ✅ Saved annotated image to: {output_path}")
        
    except Exception as e:
        print(f"   ❌ Could not draw boxes: {e}")

def run_batch_test():
    # Create output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print(f"🚀 Starting Batch Test on folder: {INPUT_FOLDER}...\n")

    # Walk through all folders
    # This finds all jpg, jpeg, and png files in subfolders
    extensions = ['*.jpg', '*.jpeg', '*.png']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(INPUT_FOLDER, '**', ext), recursive=True))

    if not image_files:
        print(f"❌ No images found in '{INPUT_FOLDER}'. Check your folder name.")
        return

    # Process each image
    for img_path in image_files:
        filename = os.path.basename(img_path)
        subfolder = os.path.basename(os.path.dirname(img_path))
        
        print(f"Processing: [{subfolder}] {filename}...")

        try:
            with open(img_path, "rb") as f:
                response = requests.post(API_URL, files={"file": f})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Print text summary
                    t_signs = data['traffic_signs']
                    g_objs = data['general_objects']
                    
                    if t_signs: print(f"   🚦 Signs: {[s['label'] for s in t_signs]}")
                    if g_objs:  print(f"   🚗 Objects: {[o['label'] for o in g_objs]}")
                    
                    # DRAW AND SAVE IMAGE
                    save_path = os.path.join(OUTPUT_FOLDER, f"result_{filename}")
                    draw_boxes(img_path, t_signs, g_objs, save_path)
                    
                else:
                    print(f"   ❌ Server Error: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Connection Failed: {e}")

if __name__ == "__main__":
    run_batch_test()