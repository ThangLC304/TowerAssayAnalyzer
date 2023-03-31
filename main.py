import os
import tkinter as tk
import json
from tkinter import ttk
from PIL import Image, ImageTk
from Libs.executor import *
from pathlib import Path
from Libs.misc import create_messagebox
from Libs.batchprocess import MY_DIR
from Libs.autoanalyzer import autoanalyzer
import openpyxl

# Predefined Constants #
ROOT = os.path.dirname(os.path.realpath(__file__))

ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']

tests = ['Novel Tank', 'Shoaling', 'Mirror Biting', 'Social Interaction', 'Predator Avoidance']
keywords = [x.split(' ')[0].lower() for x in tests]
task_json_dict = {tests[i]: keywords[i] for i in range(len(tests))}    

SELECTED_TEST = 'Select Test'

ROUND_UP = 4

COLORS = {
    'background': 'white',
    'foreground': 'black',
    'button_bg': '#F0F0F8',
    'button_fg': 'black',
    'combo_bg': '#F0F0F8',
    'combo_fg': 'black',
}

BUTTON_TEXTS = {
    'select_file': 'Select File',
    'execute': 'Execute Calculation',
    'auto': 'Auto Analyzer',
    'quit': 'Quit',
}

combobox_config = {
    'font': ('Helvetica', 12, 'bold'),
    'width': 20,
    'justify': 'center',
    'state': 'readonly',
    'background': COLORS['combo_bg'],
    'foreground': COLORS['combo_fg'],
}

button_config = {
    'bg': COLORS['button_bg'],
    'fg': COLORS['button_fg'],
    'font': ('Helvetica', 12, 'bold'),
    'width': 16,
    'justify': 'center',
    'activebackground': COLORS['button_fg'],
    'activeforeground': COLORS['button_bg'],
    'borderwidth': 5,
    'padx': 10,
    'pady': 20,
}

#####################################################

# FUNCTIONS #


def notify(task):
    
    print()
    print("="*50)
    print(f"Executing {task} Test, please wait...")
    print("="*50)
    print()


def load_files():
    global file_path
    file_path = tk.filedialog.askopenfilename(initialdir="./input", title="Select files", filetypes=[("Text Files", "*.txt")])
    file_path = Path(file_path)





def excel_export(result_dict, name = None):

    # Export the result to an excel file
    Input_path = Path(file_path)

    # Set the output file name
    if name == None:
        Ori_Output_path = Input_path.parent / (Input_path.stem + "_result.xlsx")
    else:
        Ori_Output_path = Input_path.parent / (Input_path.stem + "_" + name + "_result.xlsx")
    
    # Check if the file already exists, if so, rename current file, adding a number to the end of the file name
    Output_path = Ori_Output_path
    suffix_num = 1
    while Output_path.exists():
        Output_path = Input_path.parent / (Ori_Output_path.stem + "_" + str(suffix_num) + '.xlsx')
        suffix_num += 1
    
    # Export the result to an excel file
    df = pd.DataFrame.from_dict(result_dict, orient='index', columns=['Categories', 'Values', 'Units'])
    df.to_excel(Output_path, index=False)
    
    # open the file to change column width to fit the content
    wb = openpyxl.load_workbook(Output_path)
    ws = wb.active
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 20
    wb.save(Output_path)

    # Display a messagebox to notify the user
    create_messagebox(root, "Exported", Input_path.parent)


def display_in(result_dict, target, wg_padx, wg_pady):

    # Make 3 canvas for the 3 columns
    result_canvas1 = tk.Canvas(target, width=400, height=400, bg=COLORS["background"])
    result_canvas1.grid(row=0, column=0, padx=wg_padx, pady=wg_pady)
    result_canvas2 = tk.Canvas(target, width=170, height=400, bg=COLORS["background"])
    result_canvas2.grid(row=0, column=1, padx=wg_padx, pady=wg_pady)
    result_canvas3 = tk.Canvas(target, width=80, height=400, bg=COLORS["background"])
    result_canvas3.grid(row=0, column=2, padx=wg_padx, pady=wg_pady)

    text_color = COLORS["foreground"]
    text_height = 30

    for i, content in enumerate(result_dict.values()):
        # tk.Label(result_canvas1, text=content[0], font=("Helvetica", 20)).grid(row=i+1, column=0, padx = wg_padx, pady = wg_pady, sticky="w")
        # tk.Label(result_canvas2, text=round(content[1], ROUND_UP), font=("Helvetica", 20)).grid(row=i+1, column=0, padx = wg_padx, pady = wg_pady)
        # tk.Label(result_canvas3, text=content[2], font=("Helvetica", 20)).grid(row=i+1, column=0, padx = wg_padx, pady = wg_pady)
        # display using result_canvas.create_text instead
        result_canvas1.create_text(10, i*text_height+text_height, text=content[0], font=("Helvetica", 20), fill=text_color, anchor="w")
        result_canvas2.create_text(10, i*text_height+text_height, text=round(content[1], ROUND_UP), font=("Helvetica", 20), fill=text_color, anchor="w")
        result_canvas3.create_text(10, i*text_height+text_height, text=content[2], font=("Helvetica", 20), fill=text_color, anchor="w")


# Button 2 is to accept the current hyperparameters and execute the calculation script in calculation.py
def execute_calculation():

    SINGLE = True
    
    # Get the selected task
    task_selected = task_variable.get()
    if task_selected == "Select Task":
        pass
    elif task_selected == "Novel Tank":
        notify(task_selected)
        json_path = f"Bin/hyp_{task_json_dict[task_selected]}.json"
        with open(json_path) as f:
            hyp_dict = json.load(f)
        ntt_segment = int(hyp_dict["SEGMENT DURATION"])
        ntt_segment_num = int(int(hyp_dict["DURATION"])/ntt_segment)
        if ntt_segment == 0:
            display_dict = noveltank_exec(file_path)[1]
            SINGLE = True
        else:
            display_dict = {}
            for i in range(ntt_segment_num):
                segment_list = noveltank_exec(file_path, segment=i)
                display_dict[segment_list[0]] = segment_list[1]
            SINGLE = False
    elif task_selected == "Shoaling":
        notify(task_selected)
        display_dict = shoaling_exec(file_path)
        SINGLE = False
    elif task_selected == "Mirror Biting":
        notify(task_selected)
        display_dict = mirrorbiting_exec(file_path)
        SINGLE = True
    elif task_selected == "Social Interaction":
        notify(task_selected)
        display_dict = socialinteraction_exec(file_path)
        SINGLE = True
    elif task_selected == "Predator Avoidance":
        notify(task_selected)
        display_dict = predatoravoidance_exec(file_path)
        SINGLE = True

    # DISPLAY THE RESULT
    wg_padx = 3
    wg_pady = 3

    if SINGLE == True:

        # Display the result on a tk.Toplevel window
        result_window = tk.Toplevel(root)
        # change the title of the window to the task selected
        result_window.title(task_selected)

        display_in(display_dict, result_window, wg_padx, wg_pady)
        excel_export(display_dict)

    else:

        tabs_num = len(display_dict)
        tab_names = list(display_dict.keys())

        result_window = tk.Toplevel(root)
        result_window.title("Result")

        # Create the tab control
        tab_control = ttk.Notebook(result_window)

        # Create the tabs
        for i in range(tabs_num):
            tab = ttk.Frame(tab_control)
            tab_control.add(tab, text=tab_names[i], padding=3)

            display_in(display_dict[tab_names[i]], tab, wg_padx, wg_pady)
            excel_export(display_dict[tab_names[i]], name = tab_names[i])

        tab_control.pack(expand=1, fill="both")


# Create a function to load the JSON file when a task is selected from the Task dropdown menu
def load_json(event=None):
    save_json

    # Clear the canvas before loading the JSON file
    for widget in hyp_input_canvas.winfo_children():
        widget.destroy()

    # Load the JSON file
    task_selected = task_variable.get()
    
    json_path = f"Bin/hyp_{task_json_dict[task_selected]}.json"
    try:
        with open(json_path) as f:
            hyp_dict = json.load(f)
    except:
        print(f'Error loading {json_path} file')
        raise SystemExit
    
    # Create input widgets for each key in the hyp_dict
    for i, key in enumerate(hyp_dict.keys()):
        pdX, pdY = 10, 10
        category_label = tk.Label(hyp_input_canvas, text=key, font=("Helvetica", 15), fg=COLORS["foreground"], bg=COLORS["background"])
        category_label.grid(row=i+1, column=0, padx=pdX, pady=pdY)
        value_entry = tk.Entry(hyp_input_canvas, font=("Helvetica", 12), bg="white")
        value_entry.insert(0, str(hyp_dict[key]))
        value_entry.grid(row=i+1, column=1, padx=pdX, pady=pdY)
        if key == "SEGMENT DURATION":
            warning_label = tk.Label(hyp_input_canvas, text="Put 0 if no segmentation needed", font=("Helvetica", 11), fg=COLORS["foreground"], bg=COLORS["background"])
            warning_label.grid(row=i+1, column=2, padx=pdX, pady=pdY)

def save_json(event=None):
    # Get the selected task
    task_selected = task_variable.get()
    if task_selected == "Select Task":
        pass
    else:
        json_path = f"Bin/hyp_{task_json_dict[task_selected]}.json"
        try:
            with open(json_path) as f:
                hyp_dict = json.load(f)
        except:
            print(f'Error loading {json_path} file')
            raise SystemExit

        # Get the new values from the input widgets
        for i, key in enumerate(hyp_dict.keys()):
            current_display = hyp_input_canvas.grid_slaves(row=i+1, column=1)[0].get()
            print(current_display)
            hyp_dict[key] = float(current_display)

        # Save the new values to the JSON file
        with open(json_path, 'w') as f:
            json.dump(hyp_dict, f, indent=4)

        print(f"Hyperparameters for {task_selected} saved to {json_path}")


def auto_analyze():
    
    # Ask to open directory of project
    PROJECT_DIR = tk.filedialog.askdirectory()
    print("Selected directory:", PROJECT_DIR)
    PROJECT_DIR = Path(PROJECT_DIR)

    total_time = autoanalyzer(PROJECT_DIR, BATCHNUM = 1)

    # Display a messagebox to notify the user
    create_messagebox(root, "Batch Analysis Completed", f"Total time taken: {total_time} seconds", button=False)

def quit_program():
    root.quit()

#####################################################

# GUI #

root = tk.Tk()
root.configure(bg='#333')
root.geometry("1200x500")
root.title("Tower Assay Analyzer")

# Load the image and create a PhotoImage object
# image = Image.open("Bin/landing.png")
image = Image.open("Bin/zebrafish02.jpg")
# image = image.resize((500, 500), Image.Resampling.LANCZOS)
# resize to height = 500, width keeping the aspect ratio
image = image.resize((int(image.size[0] * 500 / image.size[1]), 500), Image.Resampling.LANCZOS)
photo_image = ImageTk.PhotoImage(image)

# Load the logo and create a PhotoImage object
logo = Image.open("Bin/logo.png")
logo = logo.resize((100, 100), Image.Resampling.LANCZOS)
logo_image = ImageTk.PhotoImage(logo)

# Create the first canvas
canvas1 = tk.Canvas(root, width=400, height=500, bg=COLORS["background"])
canvas1.pack(side="left", fill="both", expand=True)

# Add the image to the first canvas
canvas1.create_image(200, 250, image=photo_image)
# add padding to canvas1, no fill
canvas1.create_rectangle(0, 0, 400, 500, outline=COLORS["background"], width=10)

# Create the second canvas
canvas2 = tk.Canvas(root, width=800, height=500, bg=COLORS["background"])
canvas2.pack(side="right", fill="both", expand=True)

# Create the top sub-canvas for the application name and logo
top_canvas = tk.Canvas(canvas2, width=800, height=120, bg=COLORS["background"])
top_canvas.pack(side="top", fill="x")

# Add the application name and logo to the top sub-canvas
text_color = "#003D9E"
top_canvas.create_text(300, 60, text="Tower Assay Analyzer", font=("Helvetica", 30), fill=text_color)
top_canvas.create_image(700, 60, image=logo_image)

# Create the bottom sub-canvas
bottom_canvas = tk.Canvas(canvas2, width=800, height=380, bg="white")
bottom_canvas.pack(side="bottom", fill="both", expand=True)

# Create the left sub-canvas for the buttons
bottom_left_canvas = tk.Canvas(bottom_canvas, width=300, height=300, bg=COLORS["background"])
bottom_left_canvas.pack(side="left", fill="both", expand=False)

# A dropdown menu to choose Task
task_variable = tk.StringVar()
task_variable.set("Select Task")
task_dropdown = ttk.Combobox(bottom_left_canvas, 
                             textvariable=task_variable, 
                             values=["Novel Tank", "Shoaling", "Mirror Biting", "Social Interaction", "Predator Avoidance"], 
                             font=("Helvetica", 15))
task_dropdown.configure(combobox_config)
task_dropdown.grid(row=0, column=0, padx=10, pady=20)

# Create the buttons
button1 = tk.Button(bottom_left_canvas, text=BUTTON_TEXTS["select_file"], command=load_files)
button1.grid(row=1, column=0)
button1.configure(button_config)


button2 = tk.Button(bottom_left_canvas, text=BUTTON_TEXTS["execute"], command=execute_calculation)
button2.grid(row=2, column=0)
button2.configure(button_config)


button3 = tk.Button(bottom_left_canvas, text=BUTTON_TEXTS["auto"], command=auto_analyze)
button3.grid(row=3, column=0)
button3.configure(button_config)


button4 = tk.Button(bottom_left_canvas, text=BUTTON_TEXTS["quit"], command=quit_program)
button4.grid(row=4, column=0)
button4.configure(button_config)

# Create the right sub-canvas for the widget to display and change hyperparameters
bottom_right_canvas = tk.Canvas(bottom_canvas, width=500, height=300, bg=COLORS["background"])
bottom_right_canvas.pack(side="right", fill="both", expand=True)

# Create a canvas to hold the hyperparameter title, and add it to the right sub-canvas, the title is always in middle
hyp_title_canvas = tk.Canvas(bottom_right_canvas, width=500, height=50, bg=COLORS["background"])
hyp_title_canvas.pack(side="top", fill="x")
hyp_title_canvas.create_text(250, 25, text="Hyperparameters", font=("Helvetica", 20), fill="black")

button_save = tk.Button(hyp_title_canvas, text='Save it')
button_save.pack(side="right", padx=10, pady=15)

# Create a canvas to hold the input widgets
hyp_input_canvas = tk.Canvas(bottom_right_canvas, width=500, height=250, bg=COLORS["background"])
hyp_input_canvas.pack(side="top", fill="both", expand=True)


# Bind the buttons to functions
task_dropdown.bind("<<ComboboxSelected>>", load_json)
button2.bind("<Button-1>", save_json)
button_save.bind("<Button-1>", save_json)


root.mainloop()








