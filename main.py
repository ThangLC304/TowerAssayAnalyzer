import tkinter as tk
import json
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from Libs.general import *

ROOT = os.path.dirname(os.path.realpath(__file__))

test_options = ['Novel Tank', 'Shoaling', 'Mirror Biting', 'Social Interaction', 'Predator Avoidance']

SELECTED_TEST = 'Select Test'

#####################################################

# GUI #

root = tk.Tk()
root.configure(bg='#333')
root.geometry("1200x500")
root.title("Tower Assay Analyzer")

# Load the image and create a PhotoImage object
image = Image.open("Bin/image.png")
image = image.resize((400, 500), Image.ANTIALIAS)
photo_image = ImageTk.PhotoImage(image)

# Load the logo and create a PhotoImage object
logo = Image.open("logo.png")
logo = logo.resize((100, 100), Image.ANTIALIAS)
logo_image = ImageTk.PhotoImage(logo)

# Create the first canvas
canvas1 = tk.Canvas(root, width=400, height=500, bg="white")
canvas1.pack(side="left", fill="both", expand=True)

# Add the image to the first canvas
canvas1.create_image(200, 250, image=photo_image)

# Create the second canvas
canvas2 = tk.Canvas(root, width=800, height=500, bg="lightgray")
canvas2.pack(side="right", fill="both", expand=True)

# Create the top sub-canvas for the application name and logo
top_canvas = tk.Canvas(canvas2, width=800, height=200, bg="blue")
top_canvas.pack(side="top", fill="x")

# Add the application name and logo to the top sub-canvas
top_canvas.create_text(400, 100, text="Tower Assay Analyzer", font=("Helvetica", 30), fill="white")
top_canvas.create_image(650, 100, image=logo_image)

# Create the bottom sub-canvas
bottom_canvas = tk.Canvas(canvas2, width=800, height=300, bg="white")
bottom_canvas.pack(side="bottom", fill="both", expand=True)

# Create the left sub-canvas for the buttons
bottom_left_canvas = tk.Canvas(bottom_canvas, width=400, height=300, bg="lightgray")
bottom_left_canvas.pack(side="left", fill="both", expand=True)

# Button 1 to Load file(s) from a default_dir
def load_files():
    files = tk.filedialog.askopenfilenames(initialdir="./input", title="Select files", filetypes=[("Text Files", "*.txt")])

button1 = tk.Button(bottom_left_canvas, text="Load Files", font=("Helvetica", 20), command=load_files, bg="red", activebackground="pink")
button1.pack(side="top", padx=50, pady=50)

# Button 2 is changed into a dropdown menu
task_variable = tk.StringVar()
task_variable.set("


if __name__ == "__main__":
    app = App()
    app.mainloop()








