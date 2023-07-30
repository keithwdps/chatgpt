from PIL import Image, ImageDraw
import os
import re
from collections import defaultdict
from rectpack import newPacker, PackingMode, PackingBin, MaxRectsBssf, MaxRectsBlsf, MaxRectsBaf
import shutil

# Increase the limit for decompression bomb warning
Image.MAX_IMAGE_PIXELS = None

input_folder = "C:\\Users\\Keith\\My Drive\\UploadKit\\processed"
output_folder = "C:\\Users\\Keith\\My Drive\\UploadKit\\Flex-Jobs"
gang_dir_path = r"C:\Users\Keith\My Drive\UploadKit\Flex-Jobs"

gang_files = []  # Initialize the list for gang file paths

for filename in os.listdir(input_folder):
    if "GANG" in filename.upper():
        source = os.path.join(input_folder, filename)
        destination = os.path.join(gang_dir_path, filename)
        shutil.move(source, destination)  # Move the file
        gang_files.append(destination)  # Store the moved file path

dpi = 300  # Set the DPI
spacing_in_inches = 0.15  # Set the desired spacing in inches

# Calculate the spacing in pixels
spacing = int(spacing_in_inches * dpi)

# Collect the dimensions of the images in the folder and group by order number
orders = defaultdict(list)
for filename in os.listdir(input_folder):
    if filename.endswith((".png", ".jpg", ".jpeg")):  # add more extensions if needed
        match = re.search(r'#(.+?)-(.+?)-', filename)
        if match:
            order_number, last_name = match.groups()
            with Image.open(os.path.join(input_folder, filename)) as img:
                width, height = img.size
                width += spacing  # Add spacing to the width
                height += spacing  # Add spacing to the height
                if width > 6750 or height > 90000:  # Check if image is larger than the bin
                    print(f"Image {filename} is too large: {width}x{height}")
                    continue  # Skip this image
                orders[order_number].append((width, height, filename, last_name))  # store filename to use later

bins = [(6850, 360000)]  # 22.5 inches wide and 300 inches height at 300 dpi

for order_number, rectangles in orders.items():
    # Sort the rectangles by area in descending order
    rectangles.sort(key=lambda r: r[0] * r[1], reverse=True)

    # Create a new packer with all the available options
    packer = newPacker(
        mode=PackingMode.Offline,
        bin_algo=PackingBin.BFF,
        pack_algo=MaxRectsBaf,
        sort_algo=lambda rects: sorted(rects, key=lambda r: r[0]*r[1], reverse=True)
    )

    # Add the rotated rectangles to packing queue
    for r in rectangles:
        width, height, filename, last_name = r
        if width > height:
            # Rotate the image dimensions (rectangle) if it's in landscape orientation
            width, height = height, width
        packer.add_rect(width, height, rid=rectangles.index(r))

    # Add the bins where the rectangles will be placed
    for b in bins:
        packer.add_bin(*b)

    # Start packing
    packer.pack()

    # Full rectangle list
    all_rects = packer.rect_list()

    # Create the output image
    max_height = max(y + h for b, x, y, w, h, rid in all_rects)
    output = Image.new('RGBA', (bins[0][0], max_height))

    # Paste the images into the output image
    for rect in all_rects:
        b, x, y, w, h, rid = rect
        filename = rectangles[rid][2]  # retrieve filename using rect id
        img = Image.open(os.path.join(input_folder, filename)).convert("RGBA")  # open the image file and convert to RGBA

        # Manually rotate the image if it was originally in landscape orientation
        if rectangles[rid][0] > rectangles[rid][1]:
            img = img.rotate(90, expand=True)

        # Paste it on the output image at the calculated position
        output.paste(img, (x + spacing // 2, y + spacing // 2), img)

    # Calculate the sheet length in inches
    sheet_length_inches = round(max_height / dpi)

    # Get the last name for the current order
    last_name = rectangles[0][3]

    # Save the image with DPI set to 300
    output_filename = f"{order_number}-{last_name}-{sheet_length_inches}.png"
    output.save(os.path.join(output_folder, output_filename), "PNG", dpi=(300, 300))

    # Remove files in the input directory
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
        os.remove(file_path)  # Use remove() to delete the file

print("PROCESS COMPLETE.")
