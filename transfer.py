from pathlib import Path
import os
import shutil
import tkinter as tk
from tkinter import filedialog
import sys

# Get the project directory from the user using a file dialog
PROJECT_DIR = tk.filedialog.askdirectory()
print("Selected directory:", PROJECT_DIR)

# Convert the project directory to a Path object
if PROJECT_DIR:
    PROJECT_DIR = Path(PROJECT_DIR)
else:
    sys.exit()

# Find all .txt files within the project directory
txt_files = PROJECT_DIR.glob("**/*.txt")

# Define the base directory for the new location
new_base_dir = Path(os.path.expanduser("~/Desktop/OnlyTXT"))

# Loop through each .txt file and copy it to the new location
for txt_file in txt_files:
    # Construct the new path by replacing the project directory with the new base directory
    new_path = new_base_dir.joinpath(*txt_file.parts[len(PROJECT_DIR.parts):])
    
    # Create the new directory structure if it doesn't already exist
    new_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy the file to the new location
    shutil.copy(txt_file, new_path)
    
    print("Copied {} to {}".format(txt_file, new_path))