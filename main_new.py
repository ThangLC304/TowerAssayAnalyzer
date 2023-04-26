import tkinter
import tkinter.messagebox
import tkinter.ttk as ttk
import customtkinter
import json
from pathlib import Path
import shutil
import os

import threading

from Libs.autoanalyzer import autoanalyzer

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


#[TODO] Add parameters for each tank                                                # DONE
#[TODO] Add GUI to input parameters for each tank                                   # DONE
#[TODO] Add a Note row for WindowInput Control (DMSO x%)                            #
#[TODO] Automatically save parameters each time the task is changed                 # DONE
#[TODO] Analyzer button will analyze the task being selected                        # DONE
#[TODO] The Cancel button currently create the project at cwd()                     # DONE
#[TODO] Let user select the range of frames within data to be analyzed              #
#[TODO] The number of the nested parameters should be dynamic                       # DONE
#[TODO] The mirror position of the tanks -> need to change the comparing conditions # DONE
#[TODO] Add a (left/right) option to RIGHT side of nested parameters                # DONE
#[TODO] Add a small button to LEFT side of nested parameters to delete              #
#[TODO] Add a batch selector                                                        #
# [BUG] A bug when just created a project then create another one then cancel       #
# [BUG] Adding more than 2 treatments causing display bug                           # FIXED
#[TODO] Change hyp format to only "MIRROR" & "SEPARATOR", " ZONE" is calculated     # DONE
#[TODO] Note can be edit directly by user, even after the Project creating step     #
#[TODO] Save before analyze                                                         # DONE
#[TODO] Add batch and treatment name to the excel file                              # DONE
#[TODO] Hyperparamater sets for Batch/TreatmentGroup                                #
#[TODO] Drag and drop video, select Test/Batch/TreatmentGroup                       #
#[TODO] Put units for each parameters                                               # DONE
#[TODO] Change the dropdown menu of ppm/ppb to manual input                         #
#[TODO] Batch menu moved next Loaded Project, ADD / DELETE buttons                  #


ROOT = Path(__file__).parent
ORI_HYP_PATH = ROOT / "Bin"
HISTORY_PATH = "History/projects.json"


ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']
CHARS = [chr(i) for i in range(65, 65+26)]

TESTLIST = ['Novel Tank Test', 
            'Shoaling Test', 
            'Mirror Biting Test',
            'Social Interaction Test',
            'Predator Test']


def get_directory(project_name):

    with open(HISTORY_PATH, "r") as file:
        projects_data = json.load(file)
    project_dir = projects_data[project_name]["DIRECTORY"]

    return project_dir

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tkinter.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tkinter.Label(tw, text=self.text, justify=tkinter.LEFT,
                      background="#ffffe0", relief=tkinter.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class ScrollableProjectList(customtkinter.CTkScrollableFrame):

    def __init__(self, master, command=None, **kwargs):

        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.project_variable = customtkinter.StringVar()
        self.project_radiobuttons = []

    def add_project(self, project_name):
        project_radiobutton = customtkinter.CTkRadioButton(
            self, text=project_name, value=project_name, variable=self.project_variable
        )
        project_radiobutton.grid(row=len(self.project_radiobuttons), column=0, pady=(0, 10), sticky="w")
        self.project_radiobuttons.append(project_radiobutton)

    def clear_projects(self):
        for radiobutton in self.project_radiobuttons:
            radiobutton.destroy()
        self.project_radiobuttons = []

    def get_selected_project(self):
        return self.project_variable.get()
    
    def select_project(self, project_name):
        for radiobutton in self.project_radiobuttons:
            if radiobutton.cget("text") == project_name:
                radiobutton.invoke()
                break


class ProjectDetailFrame(customtkinter.CTkFrame):

    def __init__(self, master, project_name, **kwargs):

        super().__init__(master, **kwargs)

        # # Create tree view
        # self.tree = ttk.Treeview(self, height = 5, show = "headings")
        # self.tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        

        # If project name is not empty, load the project details, 
        # otherwise, display "No project selected"
        self.project_name = project_name
        if self.project_name != "":
            self.load_project_details()
        else:
            label = customtkinter.CTkLabel(self, text="No project selected")
            label.grid(row=0, column=0, padx=5, pady=5)

    def update_grid_weight(self):
        rows, cols = self.grid_size()

        for row in range(rows):
            self.grid_rowconfigure(row, weight=1)

        for col in range(cols):
            self.grid_columnconfigure(col, weight=1)

    def load_project_details(self, project_name=None):

        print('Loading.. project name = ', project_name)

        if project_name == "":
            label = customtkinter.CTkLabel(self, text="No project selected")
            label.grid(row=0, column=0, padx=5, pady=5)
            return

        if project_name is not None:
            self.project_name = project_name

        with open("History/projects.json", "r") as file:
            projects_data = json.load(file)

        project_data = projects_data[self.project_name]["TREATMENTS"]

        print(project_data)

        headers = ["Treatment", "Dose", "Dose Unit", "Fish Number", "Note"]

        # scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        # scroll.grid(row=0, column=1, sticky="ns")  # Changed from scroll.pack to scroll.grid

        # self.tree.configure(yscrollcommand=scroll.set)

        # for i, header in enumerate(headers):
        #     self.tree.heading(i, text=header)
        #     self.tree.column(i, width=100, anchor='center')

        # for details in project_data.values():
        #     treatment_name, dose, dose_unit, fish_number, note = details

        #     dose = dose if dose != 0 else ""
        #     dose_unit = dose_unit if dose_unit != "" else ""
        #     fish_number = fish_number if fish_number != 0 else ""

        #     labels = [treatment_name, dose, dose_unit, fish_number, note]

        #     self.tree.insert("", "end", values=labels)

        for i, header in enumerate(headers):
            label = customtkinter.CTkLabel(self, text=header, font=customtkinter.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=5, pady=5)

        for row, (treatment, details) in enumerate(project_data.items(), start=1):
            treatment_name, dose, dose_unit, fish_number, note = details

            dose = dose if dose != 0 else ""
            dose_unit = dose_unit if dose_unit != "" else ""
            fish_number = fish_number if fish_number != 0 else ""

            labels = [treatment_name, dose, dose_unit, fish_number, note]

            for col, label_text in enumerate(labels):
                label = customtkinter.CTkLabel(self, text=label_text)
                label.grid(row=row, column=col, padx=5, pady=5)

        self.update_grid_weight()

    def clear(self):
        for child in self.winfo_children():
            child.destroy()


class Parameters(customtkinter.CTkFrame):

    def __init__(self, master, project_name, selected_task, nested_key, *args, **kwargs):
        
        super().__init__(master, *args, **kwargs)

        self.project_name = project_name
        self.selected_task = selected_task

        if self.project_name == "":
            label = customtkinter.CTkLabel(self, text="No project selected")
            label.grid(row=0, column=0, padx=5, pady=5)
        else:
            self.load_parameters(nested_key = nested_key)

        self.entries = {}

        self.UNITS = {
            "FPS": "",
            "DURATION": "seconds",
            "CONVERSION RATE": "",
            "ZONE WIDTH": "cm",
            "SEGMENT DURATION": "seconds",
        }

    def get_hyp_path(self, project_dir, selected_task_init, condition, batch_num, mode = 'single'):

        assert mode in ['single', 'multiple']

        hyp_name = f"hyp_{selected_task_init}.json"

        if mode == 'single':

            hyp_path = project_dir / 'static' / f"Batch {batch_num}" / condition / hyp_name

            return [hyp_path]
        
        elif mode == 'multiple':
            
            hyp_paths = []

            hyp_batch_dir = project_dir / 'static' / f"Batch {batch_num}"

            # find all subdirectory in hyp_batch_dir
            for sub_dir in hyp_batch_dir.iterdir():
                if sub_dir.is_dir():
                    hyp_path = sub_dir / hyp_name
                    hyp_paths.append(hyp_path)

            return hyp_paths


    def load_parameters(self, project_name=None, selected_task=None, condition = None, batch_num=None, nested_key=0):

        self.entries = {}

        self.clear()

        if project_name == None:
            project_name = self.project_name

        if selected_task is not None:
            self.selected_task = selected_task

        self.selected_task = self.selected_task.split()[0].lower()
        hyp_name = f"hyp_{self.selected_task}.json"

        if project_name == "":
            self.hyp_path = ORI_HYP_PATH / hyp_name
        else:
            project_dir = get_directory(project_name)
            self.hyp_path = self.get_hyp_path(project_dir, self.selected_task, condition, batch_num)[0]

        with open(self.hyp_path, "r") as file:
            ori_dict = json.load(file)

        # find the nested keys
        nested_keys = []
        for key, value in ori_dict.items():
            if isinstance(value, dict):
                nested_keys.append(key)

        if nested_key == 0:
            display_dict = {k: v for k, v in ori_dict.items() if not isinstance(v, (dict, list))}

            headers = ["Parameter", "Value", "Unit"]
        else:
            try:
                nested_key = nested_keys[nested_key-1]
                

            except IndexError:
                label = customtkinter.CTkLabel(self, text="No more nested keys")
                label.grid(row=0, column=0, padx=5, pady=5) 
                return "None"
            
            display_dict = ori_dict[nested_key]

            example_value = list(display_dict.values())[0]
            if isinstance(example_value, list):
                headers = ["Tank", "Value", "Left/Right"]
            else:
                headers = ["Tank", "Value"]

        example_key = list(display_dict.keys())[0]
        try:
            _ = int(example_key)
            pass
        except ValueError:
            units = [self.UNITS[k] for k in display_dict.keys()]
            for i, unit in enumerate(units):
                unit_label = customtkinter.CTkLabel(self, text=unit)
                unit_label.grid(row=i+1, column=2, padx=(5,10), pady=5)

        for row, (key, value) in enumerate(display_dict.items()):
            key_label = customtkinter.CTkLabel(self, text=key)
            key_label.grid(row=row+1, column=0, padx=5, pady=5)

            # if value is a list
            if isinstance(value, list):
                LR_switch = customtkinter.CTkSwitch(self, text=None)
                LR_switch.grid(row=row+1, column=2, padx=(5,0), pady=5)
                if int(value[1]) == 1:
                    LR_switch.select()

                display_value = value[0]
                # headers = ["Tank", "Value", "Left/Right"]
            else:
                display_value = value
                # headers = ["", "Value"]

            value_entry = customtkinter.CTkEntry(self)
            value_entry.insert(0, display_value)
            value_entry.grid(row=row+1, column=1, padx=5, pady=5)

            try:
                _ = int(key)
                entry_key = f"{nested_key}_{key}"
            except ValueError:
                entry_key = key

            if isinstance(value, list):
                self.entries[entry_key] = [value_entry, LR_switch]
            else:
                self.entries[entry_key] = value_entry

        # make a header
            for i, header in enumerate(headers):
                label = customtkinter.CTkLabel(self, text=header, font=customtkinter.CTkFont(weight="bold"))
                label.grid(row=0, column=i, padx=5, pady=5)

        return nested_key

    def clear(self):
        for child in self.winfo_children():
            child.destroy()

    def save_parameters(self, project_name, selected_task, condition, batch_num, mode = 'single'):

        assert mode in ['single', 'multiple'] 

        def get_entry(entry_dict):
            out_dict = {}
            for key, value in entry_dict.items():
                try:
                    if isinstance(value, list):
                        v = [value[0].get(), value[1].get()]
                    else:
                        v = value.get()
                except AttributeError:
                    print(f"AttributeError: {key} is not a tkinter entry")
                    print(f"Value: ", v)
                    print(f"Value type: ", type(v))
                    continue
                out_dict[key] = v
            return out_dict
        
        selected_task = self.selected_task.split()[0].lower()

        if project_name == "":
            tkinter.messagebox.showerror("Error", "No project selected.")
            return            
        else:
            project_dir = get_directory(project_name)
            hyp_paths = self.get_hyp_path(project_dir, self.selected_task, condition, batch_num, mode=mode)


        # Get the values from the entries
        updated_values = get_entry(self.entries)
        
        for hyp_path in hyp_paths:

            # load the original data
            with open(hyp_path, "r") as file:
                parameters_data = json.load(file)

            # Update the values in the dictionary with the new values
            for key, value in updated_values.items():
                try:
                    if "_" not in key:
                        parameters_data[key] = value
                    else:
                        nested_key, nested_key_value = key.split("_")
                        if nested_key not in parameters_data:
                            parameters_data[nested_key] = {}
                        parameters_data[nested_key][nested_key_value] = value

                except ValueError:
                    print(f"Invalid input for {key}: {value}. Skipping.")

            # Save the updated data to the file
            with open(hyp_path, "w") as file:
                json.dump(parameters_data, file, indent=4)

            print(f"Parameters of {selected_task} saved to {hyp_path}.")


class App(customtkinter.CTk):

    def __init__(self):

        super().__init__()

        # PREDEFINED VARIABLES
        self.PROJECT_CREATED = False
        self.CURRENT_PROJECT = ""
        # self.CURRENT_PARAMS = {}
        self.TESTLIST = TESTLIST
        self.PREVIOUS_TEST = ""

        # configure window
        self.title("Tower Assay Analyzer")
        self.geometry(f"{1440}x{790}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0) 
        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        ### COLUMN 0 ###

        button_config = {"font": ('Helvetica', 16), "width": 150, "height": 40}

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Tower Assay Analyzer", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Create Project", 
                                                        command=self.create_project)
        self.sidebar_button_1.configure(**button_config)
        self.sidebar_button_1.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Load Project", 
                                                        command=self.load_project)
        self.sidebar_button_2.configure(**button_config)
        self.sidebar_button_2.grid(row=2, column=0, columnspan=2, padx=20, pady=20)

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Delete Project", 
                                                        command=self.delete_project)
        self.sidebar_button_3.configure(**button_config)
        self.sidebar_button_3.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

        self.batch_label = customtkinter.CTkLabel(self.sidebar_frame, text="Batch Number", font=customtkinter.CTkFont(size=16))
        self.batch_label.grid(row=4, column=0, padx=5, pady=5)
        self.batch_entry = customtkinter.CTkEntry(self.sidebar_frame, width=50, height=10)
        self.batch_entry.grid(row=4, column=1, padx=5, pady=5)
        # set default value = 1
        self.batch_entry.insert(0, "1")

        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="Import Trajectories", 
                                                        command=self.import_trajectories)
        self.sidebar_button_4.configure(**button_config)
        self.sidebar_button_4.grid(row=5, column=0, columnspan=2, padx=20, pady=20)

        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, text="Analyze", 
                                                        command=self.analyze_project_THREADED)
        self.sidebar_button_5.configure(**button_config)
        self.sidebar_button_5.grid(row=6, column=0, columnspan=2, padx=20, pady=20)


        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, columnspan=2, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        
        self.appearance_mode_optionemenu.grid(row=8, column=0, columnspan=2, padx=20, pady=(10, 10))
        
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=9, column=0, columnspan=2, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=10, column=0, columnspan=2, padx=20, pady=(10, 20))

        ### COLUMN 1 ###

        container_1 = customtkinter.CTkFrame(self)
        container_1.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        container_1.grid_rowconfigure(0, weight=0)
        container_1.grid_rowconfigure(1, weight=1)
        container_1.grid_columnconfigure(0, weight=0)

        # Top part
        container_2_top = customtkinter.CTkFrame(container_1)
        container_2_top.grid(row=0, column=0, sticky="nsew")

        project_previews_label = customtkinter.CTkLabel(container_2_top, text="Project List", font=customtkinter.CTkFont(size=20, weight="bold"))
        project_previews_label.grid(row=0, column=0)

        # Bottom part
        bottom_part = customtkinter.CTkFrame(container_1)
        bottom_part.grid(row=1, column=0, sticky="nsew")

        bottom_part.grid_rowconfigure(0, weight=1)
        bottom_part.grid_rowconfigure(1, weight=0)

        self.scrollable_frame = ScrollableProjectList(bottom_part)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")

        refresh_button = customtkinter.CTkButton(bottom_part, text="Refresh", command=self.refresh_projects)
        refresh_button.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Initial refresh to populate the list
        self.refresh_projects()

        self.project_detail_container = ProjectDetailFrame(self, self.CURRENT_PROJECT, width = 400)
        self.project_detail_container.grid(row=1, column = 1, columnspan=3, padx=20, pady=20, sticky="nsew")

        ### COLUMN 2 ###

        # Create a canvas to hold the project parameters

        container_2 = customtkinter.CTkFrame(self, width = 400)
        container_2.grid(row=0, column=2, columnspan = 2, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Top part is a dropdown menu to select type of test


        container_2_top = customtkinter.CTkFrame(container_2)
        container_2_top.grid(row=0, column=0, columnspan=3, sticky="nsew")

        Header = customtkinter.CTkLabel(container_2_top, text="Loaded Project:", anchor="w", font=customtkinter.CTkFont(size=15, weight="bold"))
        Header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.LoadedProject = customtkinter.CTkLabel(container_2_top, text="None", anchor="w", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.LoadedProject.grid(row=0, column=1, columnspan=2, padx=20, pady=(20, 10), sticky="nsew")
        
        self.TestOptions = customtkinter.CTkOptionMenu(container_2, dynamic_resizing=False, 
                                                  width=210, values=self.TESTLIST)
        self.TestOptions.grid(row=1, column=0, columnspan = 2, padx=20, pady=(20, 10), sticky="nsew")

        self.save_button = customtkinter.CTkButton(container_2, text="Save", width = 50,
                                                   command=self.save_parameters)
        self.save_button.grid(row=1, column=2, padx=20, pady=20, sticky="nsew")

        self.parameters_frame = Parameters(container_2, self.CURRENT_PROJECT, self.TESTLIST[0], 0)
        self.parameters_frame.grid(row=2, columnspan=3, padx=20, pady=(10, 20), sticky="nsew")

        # write a notification to the user to say 
        # Line 1: "Please click save in each Task selected before changing to next Task."
        # Line 2: "Changing to a new Task will not automatically save any changes made to the previous Task."
        ### COLUMN 3+ ###

        container_3 = customtkinter.CTkFrame(self, width = 400)
        container_3.grid(row=0, column=5, columnspan = 2, padx=(20, 0), pady=(20, 0), sticky="nsew")

        self.nested_key_1_header = customtkinter.CTkLabel(container_3, text="None", anchor="w", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.nested_key_1_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.nested_key_1_frame = Parameters(container_3, self.CURRENT_PROJECT, self.TESTLIST[0], 1)
        self.nested_key_1_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")

        self.nested_key_2_header = customtkinter.CTkLabel(container_3, text="None", anchor="w", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.nested_key_2_header.grid(row=0, column=2, padx=20, pady=(20, 10), sticky="nsew")
        self.nested_key_2_frame = Parameters(container_3, self.CURRENT_PROJECT, self.TESTLIST[0], 2)
        self.nested_key_2_frame.grid(row=1, column=2, columnspan = 2, padx=20, pady=(10, 20), sticky="nsew")

        self.TestOptions.configure(command=self.on_test_selected)

        # Load the first test by default
        self.on_test_selected(load_type = "first_load")



    ### COL 2 ROW 0 ###

    # Function to handle when a new test is selected
    def on_test_selected(self, selected_test=None, load_type="not_first_load"):
        assert load_type in ["not_first_load", "first_load"]

        if load_type == "first_load":
            selected_test = self.TESTLIST[0]
        else:
            self.save_parameters(mode = "previous")

        print("Current Project: ", self.CURRENT_PROJECT)

        self.parameters_frame.load_parameters(project_name = self.CURRENT_PROJECT, selected_task = selected_test, nested_key = 0)
        nested_key_1 = self.nested_key_1_frame.load_parameters(project_name = self.CURRENT_PROJECT, selected_task = selected_test, nested_key = 1)
        nested_key_2 = self.nested_key_2_frame.load_parameters(project_name = self.CURRENT_PROJECT, selected_task = selected_test, nested_key = 2)

        self.LoadedProject.configure(text=self.CURRENT_PROJECT)
        self.nested_key_1_header.configure(text=nested_key_1)
        self.nested_key_2_header.configure(text=nested_key_2)

        self.PREVIOUS_TEST = selected_test


    def save_parameters(self, mode = "current"):
        assert mode in ["current", "previous"]

        if mode == "current":
            # Get the selected test type
            selected_test = self.TestOptions.get()
        else:
            selected_test = self.PREVIOUS_TEST

        # Save the parameters
        self.parameters_frame.save_parameters(project_name = self.CURRENT_PROJECT, selected_task = selected_test)
        self.nested_key_1_frame.save_parameters(project_name = self.CURRENT_PROJECT, selected_task = selected_test)
        self.nested_key_2_frame.save_parameters(project_name = self.CURRENT_PROJECT, selected_task = selected_test)


    
    # def load_parameter(self, event):

    #     # Get the selected test type
    #     selected_test = event.widget.get()
    #     print(selected_test)

    #     # Clear the existing parameters
    #     self.project_detail_container.clear()

    #     # Load the new parameters
    #     self.project_detail_container.load_project_details(self.CURRENT_PROJECT, selected_test)



    ### DELETE PROJECT BUTTON FUNCTION ###

    def delete_project(self):

        # Get the selected project
        selected_project = self.scrollable_frame.get_selected_project()

        if selected_project == "":
            tkinter.messagebox.showerror("Error", "Please select a project")
            return

        # Delete the project from the history file
        with open(HISTORY_PATH, "r") as file:
            projects_data = json.load(file)

        project_dir = projects_data[selected_project]["DIRECTORY"]

        # Delete the project directory
        shutil.rmtree(project_dir)

        del projects_data[selected_project]

        with open(HISTORY_PATH, "w") as file:
            json.dump(projects_data, file, indent=4)

        print("Deleted project: ", selected_project)

        self.CURRENT_PROJECT = ""

        print("Set current project to blank")

        # Refresh the project list
        print("Refresh projects")
        self.refresh_projects()

        # Refresh the project details
        print("Refresh projects detail")
        self.refresh_projects_detail()

    



    ### LOAD PROJECT BUTTON FUNCTION ###

    def refresh_projects_detail(self):
        # Clear existing project details labels
        self.project_detail_container.clear()

        # Reload the project details
        self.project_detail_container.load_project_details(self.CURRENT_PROJECT)
        

    def load_project(self):
        selected_project = self.scrollable_frame.get_selected_project()
        self.CURRENT_PROJECT = selected_project

        print("current project: ", self.CURRENT_PROJECT)

        self.refresh_projects_detail()

        self.on_test_selected(load_type = "first_load")


    ### CREATE PROJECT BUTTON FUNCTION ###

    def create_project(self):
        self.project_input_window()

        if self.PROJECT_CREATED:

            with open(HISTORY_PATH, "r") as file:
                projects_data = json.load(file)

            # latest_project = list(projects_data.keys())[-1]
            print(f"Project name: {self.CURRENT_PROJECT}")
            for treatment, details in projects_data[self.CURRENT_PROJECT].items():
                print(f"{treatment}: {details}")

            self.refresh_projects()
            # select the newly created project in the list
            self.scrollable_frame.select_project(self.CURRENT_PROJECT)

            self.save_project()

        else:
            print("Project not created")


    def refresh_projects(self):
        # Clear existing project labels
        self.scrollable_frame.clear_projects()

        # Read the projects.json file and add project names to the list
        try:
            with open(HISTORY_PATH, "r") as file:
                projects_data = json.load(file)
        except:
            print("No projects found or no record of projects")
            return

        for project_name in projects_data.keys():
            self.scrollable_frame.add_project(project_name)


    def directories_maker(self, project_dir, batch_num):

        if os.path.exists(project_dir):
            return
        else:
            os.mkdir(project_dir)

        # turn batch_num into ordinal
        batch = ORDINALS[int(batch_num)-1]

        # change number 2 into B, using mathematically

        with open(HISTORY_PATH, "r") as file:
            projects_data = json.load(file)

        treatments = projects_data[self.CURRENT_PROJECT]["TREATMENTS"]

        all_paths = {}

        all_paths['Parent'] = []
        for i, test in enumerate(self.TESTLIST):
            temp = f"0{i+1} - {test}"
            all_paths['Parent'].append(temp)
        
        normal_parents = []
        group_parents = []
        for path in all_paths['Parent']:
            if "Shoaling" in path:
                group_parents.append(path)
            else:
                normal_parents.append(path)

        shoaling_tank_count = 0
        other_tank_count = 0

        for k, v in treatments.items():
            char = k.split()[1]
            if char == "A":
                tail = f"A - Control ({batch} Batch)"
            else:
                # check type of v[1]
                if float(v[1]) >= 10:
                    v[1] = str(int(float(v[1])))
                else:
                    v[1] = str(float(v[1]))
                tail = f"{char} - {v[1]} {v[2]} ({batch} Batch)"

            fish_num = int(v[3])
            if fish_num > other_tank_count:
                other_tank_count = fish_num
            all_paths[f"Child-{char}"] = [f"{parent}\\{tail}" for parent in all_paths['Parent']]
            for i in range(1, fish_num+1):
                all_paths[f"Child-{char}"].extend([f"{parent}\\{tail}\\{i}" for parent in normal_parents])
            
            fish_group = fish_num // 3
            if fish_group > shoaling_tank_count:
                shoaling_tank_count = fish_group
            for i in range(1, fish_group+1):
                all_paths[f"Child-{char}"].extend([f"{parent}\\{tail}\\{i}" for parent in group_parents])

        for k, v in all_paths.items():
            for path in v:
                os.makedirs(os.path.join(project_dir, path))

        return shoaling_tank_count, other_tank_count

    def save_project(self):
        # selected_project = self.scrollable_frame.get_selected_project()
        # self.CURRENT_PROJECT = selected_project

        save_dir = tkinter.filedialog.askdirectory()
        save_dir = Path(save_dir)

        project_dir = save_dir / self.CURRENT_PROJECT
        # project_dir.mkdir(parents=True, exist_ok=True)

        shoaling_tank_count, other_tank_count = self.directories_maker(project_dir, 1)
        print(f"shoaling_tank_count: {shoaling_tank_count}")
        print(f"other_tank_count: {other_tank_count}")

        with open(HISTORY_PATH, "r") as file:
            projects_data = json.load(file)
        
        # save the directory of the project to the projects_data
        projects_data[self.CURRENT_PROJECT]["DIRECTORY"] = str(project_dir)

        with open(HISTORY_PATH, "w") as file:
            json.dump(projects_data, file, indent=4)

        #clone the hyp_{}.json file to static_path
        ori_static_path = Path(__file__).parent / "Bin"
        project_static_path = project_dir / "static"
        project_static_path.mkdir(parents=True, exist_ok=True)

        # take all the files start with "hyp_" and end with ".json" from ori_static_path
        # and copy them to project_static_path
        for file in ori_static_path.glob("hyp_*.json"):
            shutil.copy(file, project_static_path)

        for file in project_static_path.glob("hyp_*.json"):
            # if not .json, skip
            if not file.suffix == ".json":
                continue
            
            if "shoaling" in file.name:
                desired_key_num = shoaling_tank_count
            else:
                desired_key_num = other_tank_count

            with open(file, "r") as f:
                data = json.load(f)
            for value in data.values():
                if not isinstance(value, dict):
                    continue

                if len(value) < desired_key_num:
                    print("Tank number is not enough, adding extra tanks")
                    # check type of value.values(), if it is a list, new_value = [0,0], else new_value = 0
                    if type(list(value.values())[0]) == list:
                        default_value = [0,0]
                    else:
                        default_value = 0
                    while len(value) < desired_key_num:
                        temp_key = chr(len(value)+65)
                        print("Adding tank: ", temp_key, "with default value: ", default_value, "to file: ", file.name, "")
                        value[temp_key] = default_value
                elif len(value) > desired_key_num:
                    print("Tank number is too much, removing extra tanks")
                    while len(value) > desired_key_num:
                        print("Removing tank")
                        value.popitem()
                else:
                    pass

            with open(file, "w") as f:
                json.dump(data, f, indent=4)


    def project_input_window(self):
        treatment_widgets = []

        bold_font = customtkinter.CTkFont(size = 15, weight="bold")

        def add_treatment():
            treatment_row = len(treatment_widgets)*3 + r + 1
            treatment_name = f"Treatment {chr(ord('C') + len(treatment_widgets))}:"

            treatment_label = customtkinter.CTkLabel(top_canvas, text=treatment_name, font=bold_font)
            treatment_label.grid(row=treatment_row, column=0, pady=(20, 5))
            treatment_entry = customtkinter.CTkEntry(top_canvas)
            treatment_entry.grid(row=treatment_row, column=1, pady=(20, 5))

            dose_label = customtkinter.CTkLabel(top_canvas, text="Dose:")
            dose_label.grid(row=treatment_row + 1, column=0, pady=5)
            dose_entry = customtkinter.CTkEntry(top_canvas)
            dose_entry.grid(row=treatment_row + 1, column=1, pady=5)
            unit_optionmenu = customtkinter.CTkOptionMenu(top_canvas, values=["ppm", "ppb"])
            unit_optionmenu.grid(row=treatment_row + 1, column=2, pady=5)

            fish_number_label = customtkinter.CTkLabel(top_canvas, text="Fish Number:")
            fish_number_label.grid(row=treatment_row + 2, column=0, pady=5)
            fish_number_entry = customtkinter.CTkEntry(top_canvas)
            fish_number_entry.grid(row=treatment_row + 2, column=1, pady=5)

            treatment_widgets.append((treatment_entry, dose_entry, unit_optionmenu, fish_number_entry))

        def get_values():
            project_name = project_name_entry.get()
            self.CURRENT_PROJECT = project_name
            try:
                note = treatment_a_entry.get()
            except:
                note = ""
            try:
                treatment_list = {
                    "Treatment A": [
                        "Control",
                        0,
                        "",
                        int(fish_number_a_entry.get()),
                        note
                    ],
                    "Treatment B": [
                        treatment_b_entry.get(),
                        float(dose_b_entry.get()),
                        unit_b_optionmenu.get(),
                        int(fish_number_b_entry.get()),
                        note
                    ]
                }
            except Exception as e:
                #show message box of error
                print(e)
                tkinter.messagebox.showerror("Error", "Please fill the required fields with right type of value")

            for i, (treatment_entry, dose_entry, unit_optionmenu, fish_number_entry) in enumerate(treatment_widgets):
                treatment_name = f"Treatment {chr(ord('C') + i)}"
                treatment_list[treatment_name] = [
                    treatment_entry.get(),
                    float(dose_entry.get()),
                    unit_optionmenu.get(),
                    int(fish_number_entry.get()),
                    note
                ]

            # Save values to projects.json
            project_data = {
                project_name: {
                    "TREATMENTS" : treatment_list
                    }
                }

            try:
                with open(HISTORY_PATH, "r") as file:
                    existing_data = json.load(file)
                if project_name in existing_data:
                    # Display message box of error
                    tkinter.messagebox.showerror("Error", "Project already exists")
                else:
                    existing_data.update(project_data)
                    self.PROJECT_CREATED = True
                    with open(HISTORY_PATH, "w") as file:
                        json.dump(existing_data, file, indent=2)
                    input_window.destroy()  # Move this line inside the else block
            except:
                existing_data = project_data
                self.PROJECT_CREATED = True
                with open(HISTORY_PATH, "w") as file:
                    json.dump(existing_data, file, indent=2)
                input_window.destroy()  # Move this line inside the except block

        def cancel_button_command():
            self.PROJECT_CREATED = False
            input_window.destroy()


        input_window = tkinter.Toplevel(self)
        # set window size
        input_window.geometry("500x500")

        input_window.title("Project Input")

        # Top Canvas
        top_canvas = customtkinter.CTkScrollableFrame(input_window, width = 380)
        # expand the canvas to fill the window
        input_window.rowconfigure(0, weight=1)
        top_canvas.grid(row=0, column=0, sticky="nsew")

        r=0
        # Project name
        project_name_label = customtkinter.CTkLabel(top_canvas, text="Project name:", font=bold_font)
        project_name_label.grid(row=r, column=0, pady=5)
        project_name_entry = customtkinter.CTkEntry(top_canvas)
        project_name_entry.grid(row=r, column=1, pady=5)

        r+=1
        # Treatment A (Control)
        treatment_a_label = customtkinter.CTkLabel(top_canvas, text="Treatment A:", font=bold_font)
        treatment_a_label.grid(row=r, column=0, pady=5)
        treatment_a_entry = customtkinter.CTkEntry(top_canvas)
        treatment_a_entry.grid(row=r, column=1, pady=5)

        hover_button = tkinter.Button(top_canvas, text="?")
        hover_button.grid(row=r, column=2, pady=5)
        CreateToolTip(hover_button, text = 'Control condition\n'
                 'Leave blank if you used pure water\n'
                 'The info you put here would be saved as Note\n'
        )

        r+=1
        # Fish number
        fish_number_a_label = customtkinter.CTkLabel(top_canvas, text="Fish Number:")
        fish_number_a_label.grid(row=r, column=0, pady=5)
        fish_number_a_entry = customtkinter.CTkEntry(top_canvas)
        fish_number_a_entry.grid(row=r, column=1, pady=5)
        
        r+=1
        # Treatment B
        treatment_b_label = customtkinter.CTkLabel(top_canvas, text="Treatment B:", font=bold_font)
        treatment_b_label.grid(row=r, column=0, pady=(20, 5))
        treatment_b_entry = customtkinter.CTkEntry(top_canvas)
        treatment_b_entry.grid(row=r, column=1, pady=(20, 5))

        r+=1
        # Dose
        dose_label = customtkinter.CTkLabel(top_canvas, text="Dose:")
        dose_label.grid(row=r, column=0, pady=5)
        dose_b_entry = customtkinter.CTkEntry(top_canvas)
        dose_b_entry.grid(row=r, column=1, pady=5)
        unit_b_optionmenu = customtkinter.CTkOptionMenu(top_canvas, values=["ppm", "ppb"])
        unit_b_optionmenu.grid(row=r, column=2, pady=5)

        r+=1
        # Fish number
        fish_number_b_label = customtkinter.CTkLabel(top_canvas, text="Fish Number:")
        fish_number_b_label.grid(row=r, column=0, pady=5)
        fish_number_b_entry = customtkinter.CTkEntry(top_canvas)
        fish_number_b_entry.grid(row=r, column=1, pady=5)

        # Bottom Canvas
        bottom_canvas = customtkinter.CTkFrame(input_window)
        bottom_canvas.grid(row=1, column=0, sticky="nsew")

        # Add button
        add_button = customtkinter.CTkButton(bottom_canvas, text="Add Treatment", 
                                             command=add_treatment)
        add_button.grid(row=0, column=0, padx=5, pady=20)

        # Confirm button
        confirm_button = customtkinter.CTkButton(bottom_canvas, text="CONFIRM", 
                                                 font = bold_font,
                                                 command=get_values)
        confirm_button.grid(row=1, column=0, padx=5, pady=20)

        # Cancel button
        cancel_button = customtkinter.CTkButton(bottom_canvas, text="CANCEL", 
                                                font = bold_font,
                                                command=cancel_button_command)
        cancel_button.grid(row=1, column=1, padx=5, pady=20)

        input_window.wait_window()

    
    ### ANALYZE BUTTON ###

    def create_progress_window(self):
        progress_window = tkinter.Toplevel(self)
        progress_window.title("Analysis Progress")
        progress_window.geometry("300x100")

        progress_label = tkinter.Label(progress_window, text="Analyzing...", font=('Helvetica', 12))
        progress_label.pack(pady=(10, 0))

        progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=200)
        progress_bar.pack(pady=(10, 20))

        return progress_bar

    def analyze_project(self):

        if self.CURRENT_PROJECT == "":
            tkinter.messagebox.showerror("Error", "Please select a project")
            return
        
        # save the current parameters
        self.save_parameters(mode='current')

        project_dir = Path(get_directory(self.CURRENT_PROJECT))

        # get selected task
        task = self.TestOptions.get()

        try:
            BATCH_NUMBER = int(self.batch_entry.get())
        except ValueError:
            BATCH_NUMBER = 1

        overwrite = False

        while True:

            progress_bar = self.create_progress_window()
            total_time, notification, ERROR = autoanalyzer(project_dir, BATCH_NUMBER, task, progress_bar, overwrite)

            if ERROR == None:
                progress_bar.master.destroy()  # Close the progress window
                tkinter.messagebox.showinfo("Analysis Complete", f"{notification}.\n Total time taken: {total_time} seconds")
                break
            elif ERROR == "Existed":
                # pop up a window to ask if the user wants to overwrite
                overwrite = tkinter.messagebox.askyesno("Warning", f"{notification}. Do you want to overwrite?")
                if overwrite:
                    progress_bar.master.destroy()
                    continue
                else:
                    progress_bar.master.destroy()
                    break
            elif ERROR == "File Opened":
                message = f"{notification}. \n Please close the file and press OK to proceed. \n Press No to cancel."
                proceed = tkinter.messagebox.askyesno("Error", message)
                if proceed:
                    progress_bar.master.destroy()
                    continue
                else:
                    progress_bar.master.destroy()
                    break

    def analyze_project_THREADED(self):

        analyze_thread = threading.Thread(target=self.analyze_project)
        analyze_thread.start()


    ### IMPORT BUTTON ###

    def import_trajectories(self):

        if self.CURRENT_PROJECT == "":
            tkinter.messagebox.showerror("Error", "Please select a project")
            return
        
        project_dir = Path(get_directory(self.CURRENT_PROJECT))

        # Get the project directory from the user using a file dialog
        ori_dir = tkinter.filedialog.askdirectory()
        print("Selected directory:", ori_dir)

        # Convert the project directory to a Path object
        if ori_dir:
            ori_dir = Path(ori_dir)
        else:
            return

        # Find all .txt files within the project directory
        txt_files = ori_dir.glob("**/*.txt")

        # change all paths in txt_files to fullpath
        txt_paths = [txt_file.resolve() for txt_file in txt_files]

        char_list = [chr(i) for i in range(65, 91)]

        def check_grandparent_format(txt_path, batch_num):
            # check if the grandparent folder of txt_path is in the format of "A - Control (1st Batch)"
            # if yes, return True, else return False

            grandparent = txt_path.parent.parent.name
            sign = grandparent.split("-")[0].strip()
            treatment = grandparent.split("-")[1].strip()
            batch_ord = treatment.split("(")[1].split(" ")[0].strip()
            # change ordinal to number, 1st -> 1
            if batch_num != int(batch_ord[:-2]):
                return None
            if sign not in char_list:
                # change it from number to letter, 1 -> A
                sign = chr(int(sign) + 64)
            
            return f"{sign} - {treatment}"

        def check_test(txt_path):
            # check if any word in name_dict.keys() is in str(txt_path).lower()
            # if yes then construct a name based on the found name
            name_dict = {
                "novel tank" : "01 - Novel Tank Test",
                "shoaling" : "02 - Shoaling Test",
                "mirror" : "03 - Mirror Biting Test",
                "social" : "04 - Social Interaction Test",
                "predator" : "05 - Predator Test"
            }

            for key in name_dict.keys():
                if key in str(txt_path).lower():
                    return name_dict[key]

        def get_project_path(txt_path, project_dir, batch_num):
            gparents = check_grandparent_format(txt_path, batch_num)
            if gparents == None:
                return None
            # if the txt_path contain "novel tank"
            ancestors = Path(check_test(txt_path)) / Path(gparents)
            # get the parent and name of txt_path
            parent = txt_path.parent.name
            file = txt_path.name
            return project_dir / ancestors / parent / file

        BATCH_NUMBER = int(self.batch_entry.get())

        # Loop through each .txt file and copy it to the new location
        for txt_path in txt_paths:
            # Construct the new path by replacing the project directory with the new base directory
            new_path = get_project_path(txt_path, project_dir, BATCH_NUMBER)

            if new_path == None:
                continue
            
            # Create the new directory structure if it doesn't already exist
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file to the new location
            shutil.copy(txt_path, new_path)
            
            print("Copied {} to {}".format(txt_path, new_path))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")


if __name__ == "__main__":
    app = App()
    app.mainloop()