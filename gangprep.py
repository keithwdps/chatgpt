import os
import shutil
import re
import subprocess
import glob

# Define the directory paths
input_dir_path = r"C:\Users\Keith\My Drive\uploadkit\output"
output_dir_path = r"C:\Users\Keith\My Drive\uploadkit\processed"
gang_dir_path = r"C:\Users\Keith\My Drive\uploadkit\Flex-Jobs"

# Create the output and gang directories if they don't exist
os.makedirs(output_dir_path, exist_ok=True)
os.makedirs(gang_dir_path, exist_ok=True)

# Iterate through every file in the input directory
for filename in os.listdir(input_dir_path):
    print(f"Processing {filename}...")

    # Skip directories
    if os.path.isdir(os.path.join(input_dir_path, filename)):
        print(f"Skipping {filename} because it is a directory.")
        continue

    # Find the quantity using regex
    match = re.search(r'(?:.*#.*#)(\d+)', filename.split('.')[0]) # Assuming filename has an extension
    if match:
        qty = int(match.group(1))
    else:
        print(f"Could not find quantity in filename {filename}. Skipping this file.")
        continue

    # Copy the file the specified number of times
    for i in range(qty):  # Start from 0 to include original file
        # Construct new filename
        base_filename = filename[:filename.index(match.group(0))] + filename[filename.index(match.group(0)) + len(match.group(0)):]
        new_filename = f"{base_filename[:-len('.png')]}_{i+1}_{filename}"
        print(f"Creating copy {i+1} of {filename} as {new_filename}")
        shutil.copy(os.path.join(input_dir_path, filename), os.path.join(output_dir_path, new_filename))

 
    print(f"Finished processing {filename}.\n")

# Now, delete all files in the input directory
files = glob.glob(os.path.join(input_dir_path, '*'))
for f in files:
    if os.path.isfile(f):
        os.remove(f)

script_path = r"C:\Users\Keith\My Drive\uploadkit\orderscript\gang.py"

subprocess.Popen(f'python "{script_path}"', shell=True)
