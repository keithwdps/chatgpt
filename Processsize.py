import os
import subprocess
import re
import shutil
from PIL import Image, ExifTags
import tkinter as tk
from tkinter import messagebox
import glob

Image.MAX_IMAGE_PIXELS = None

def copy_files_and_run_script():
    src_dir = "c:\\users\\keith\\my drive\\Uploadkit"
    dst_dir = "c:\\users\\keith\\my drive\\Uploadkit\\originals"

    os.makedirs(dst_dir, exist_ok=True)
        
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        
        if os.path.isfile(src_file) and not os.path.samefile(src_file, dst_dir):  
            dst_file = os.path.join(dst_dir, filename)
            shutil.copy(src_file, dst_file)
            print(f"Copied file {filename} to processed directory")

def change_image_dpi(folder):
    for filename in os.listdir(folder):
        if filename.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")) and 'gang' not in filename.lower():
            image = Image.open(os.path.join(folder, filename))
            width, height = image.size
            new_image = image.resize((width, height), Image.LANCZOS)
            new_image.save(os.path.join(folder, filename), dpi=(300, 300))
            print(f"Filename: {filename}, New DPI: 300, 300")

def create_report(folder):
    report_file = os.path.join(os.path.expanduser('~'), 'Desktop', 'image_report.txt')
    report_text = "Filename, DPI, Transparency\n"

    for filename in os.listdir(folder):
        if filename.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")):
            filepath = os.path.join(folder, filename)
            image = Image.open(filepath)

            dpi = image.info.get('dpi', (0, 0))

            transparency = 'Yes' if image.mode in ('RGBA', 'LA') and image.getchannel('A').getextrema() != (255, 255) else 'No'

            report_text += f"{filename}, {dpi}, {transparency}\n"

    with open(report_file, 'w') as report:
        report.write(report_text)

    return report_text

def crop_and_resize(file_path, resize_value, output_directory):
    image = Image.open(file_path)
    cropped_image = image.crop(image.getbbox())
    contracted_image = cropped_image.crop((2, 2, cropped_image.width - 2, cropped_image.height - 2))
    target_size_in_mm = float(resize_value)
    new_width = int(target_size_in_mm * (300/25.4))
    aspect_ratio = new_width / contracted_image.width
    new_height = int(contracted_image.height * aspect_ratio)
    resized_image = contracted_image.resize((new_width, new_height))
    output_path = os.path.join(output_directory, os.path.basename(file_path))
    resized_image.save(output_path, dpi=(300,300))
    print(f"Processed and saved {file_path} as {output_path} with physical width {target_size_in_mm} mm")

def process_files(source_directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)
    filenames = os.listdir(source_directory)

    for filename in filenames:
        match = re.search(r'#\w+-\w+-(\d+)#\w+', filename)
        if match:
            print(f"Found match in filename {filename}: size = {match.group(1)} mm")
            file_path = os.path.join(source_directory, filename)
            try:
                crop_and_resize(file_path, match.group(1), output_directory)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

def move_files():
    source_dir = r'C:\Users\Keith\My Drive\uploadkit'
    target_dir = r'C:\Users\Keith\My Drive\uploadkit\output'

    files = os.listdir(source_dir)

    for filename in files:
            if 'gang' in filename.lower():
                    src_file = os.path.join(source_dir, filename)
                    flexi_file = os.path.join(target_dir, filename)
                    shutil.move(src_file, flexi_file)
                    print(f"Moved file {filename} to Flexi directory")

def delete_files():
    source_dir = r'C:\Users\Keith\My Drive\uploadkit'
    files = glob.glob(os.path.join(source_dir, '*'))
    for f in files:
       if os.path.isfile(f):
            os.remove(f)
    print("Files deleted.")

def run_script():
    script_path = r'C:\Users\Keith\My Drive\uploadkit\orderscript\gangprep.py'
    subprocess.call(["python", script_path])
    print("Starting Gang Process.")

def main():
    folder = r'C:\Users\Keith\My Drive\uploadkit'
    copy_files_and_run_script()
    change_image_dpi(folder)
    report_text = create_report(folder)
    move_files()
    source_directory = r'C:\Users\Keith\My Drive\uploadkit'
    output_directory = r'C:\Users\Keith\My Drive\uploadkit\output'
    process_files(source_directory, output_directory)
    delete_files()
    run_script()

    # create a popup message
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Image Report", report_text)
    root.destroy()

if __name__ == "__main__":
    main()
