import tkinter
import tkinter.messagebox
import tkinter.ttk as ttk
import customtkinter
import os
from pathlib import Path
import shutil

PROJECT_DIR = Path(r"D:\TestSave\M1")


ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']
CHARS = [chr(i) for i in range(65, 65+26)]
video_types = [".mp4", ".avi", ".mkv"]
filetypes=[("Video Files", " ".join(["*" + t for t in video_types]))]

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class VideoWidgets:
    def __init__(self, master, display_frame, PROJECT_DIR = PROJECT_DIR, 
                 list1=["01 - Novel Tank Test", "02 - Shoaling Test", "03 - Mirror Biting Test", "04 - Social Interaction Test", "05 - Predator Avoidance Test"], 
                 list2=["Control", "Treatment X", "Treatment Y"], 
                 list3=["1st", "2nd"]
                 ):

        self.PROJECT_DIR = PROJECT_DIR

        self.list1 = list1
        self.list2 = list2
        self.list3 = list3

        label_font = ("Times New Roman", 14, "bold")
        self.label1 = customtkinter.CTkLabel(master, text="Test", font=label_font)
        self.label2 = customtkinter.CTkLabel(master, text="Treatment", font=label_font)
        self.label3 = customtkinter.CTkLabel(master, text="Batch", font=label_font)

        self.dropdown_1 = customtkinter.CTkOptionMenu(master, values=self.list1)
        self.dropdown_2 = customtkinter.CTkOptionMenu(master, values=self.list2)
        self.dropdown_3 = customtkinter.CTkOptionMenu(master, values=self.list3)

        self.import_button = customtkinter.CTkButton(master, text="Import")
        self.import_button.configure(command=self.on_import_click)
        self.remove_button = customtkinter.CTkButton(master, text="Remove", command=self.on_remove_click)


        self.origin_path = None
        self.selected_row = None
        self.display_frame = display_frame

    def grid(self, row):
        pdx = 10
        pdy = 5
        self.label1.grid(row=row, column=0, padx=pdx, pady=pdy)
        self.label2.grid(row=row, column=1, padx=pdx, pady=pdy)
        self.label3.grid(row=row, column=2, padx=pdx, pady=pdy)
        self.dropdown_1.grid(row=row+1, column=0, padx=pdx, pady=pdy)
        self.dropdown_2.grid(row=row+1, column=1, padx=pdx, pady=pdy)
        self.dropdown_3.grid(row=row+1, column=2, padx=pdx, pady=pdy)
        self.import_button.grid(row=row+1, column=3, padx=pdx, pady=pdy)
        self.remove_button.grid(row=row+1, column=4, padx=pdx, pady=pdy)

    
    def get_output_path(self, test=None, treatment=None, batch=None):

        ALL_TESTS = ['Novel Tank', 'Shoaling', 'Mirror Biting', 'Social Interaction', 'Predator Avoidance']

        if not test:
            test = self.dropdown_1.get()
        if not treatment:
            treatment = self.dropdown_2.get()
        if not batch:
            batch = self.dropdown_3.get()

        print("test:", test)
        print("treatment:", treatment)
        print("batch:", batch)

        test_index = self.list1.index(test)
        test = ALL_TESTS[test_index]

        treatment_index = self.list2.index(treatment)
        treatment = CHARS[treatment_index] # A -> A

        if not batch:
            batch = "1"
        batch_index = self.list3.index(batch)
        batch = ORDINALS[batch_index] # 1 -> 1st

        # In PROJECT DIR, use glob to find folder that contain test.lower()
        # return the first folder that contains test.lower()

        test_folder = [f for f in self.PROJECT_DIR.glob("*") if test.lower() in f.name.lower()][0]
        test_dir = self.PROJECT_DIR / test_folder
        # print(f"Found test folder: {test_dir}")

        # In test_dir, use glob to find folder that startwith treatment.lower() and contain batch.lower()
        # return the first folder that contains treatment.lower() and batch.lower()

        treatment_folder = [f for f in test_dir.glob("*") if f.is_dir() and f.name.lower().startswith(treatment.lower()) and batch.lower() in f.name.lower()][0]
        treatment_dir = test_dir / treatment_folder
        # print(f"Found treatment folder: {treatment_dir}")

        # In treatment_dir, use glob to find all folders that their name is a integer number
        # return list of them

        fish_folders = [f for f in treatment_dir.glob("*") if f.is_dir() and f.name.isdigit()]
        fish_dirs = [treatment_dir / f for f in fish_folders]
        # print(f"Found fish folders: {fish_dirs}")

        video_contained_dirs = []
        # Check within these folders, if there is a folder that contains the video file
        for fish_dir in fish_dirs:
            video_files = [f for f in fish_dir.glob("*") if f.is_file() and f.suffix.lower() in video_types]
            if video_files:
                video_contained_dirs.append(fish_dir)

        return fish_dirs, video_contained_dirs

        
    def on_import_click(self):
        file_path = tkinter.filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
        if file_path:
            self.origin_path = file_path

            # Add the new row to the top frame
            values = (self.dropdown_1.get(), self.dropdown_2.get(), self.dropdown_3.get(), file_path)
            self.display_frame.add_row(values)

    def on_remove_click(self):
        self.display_frame.remove_row()

    def select_row(self, treeview):
        selected_items = treeview.selection()
        if selected_items:
            self.selected_row = selected_items[0]
        else:
            self.selected_row = None


class VideoAdd(tkinter.Toplevel):
    def __init__(self, master, PROJECT_DIR):
        super().__init__(master)

        self.PROJECT_DIR = PROJECT_DIR

        self.title("VideoAdd")
        # move to center of screen
        self.minsize(400, 400)
        self.geometry("+%d+%d" % (self.winfo_screenwidth()/2 - 400, self.winfo_screenheight()/2 - 300))
        self.rowconfigure(0, weight=1)

        self.create_widgets()

        # Initialize Treeview in __init__ method
        self.treeview_height = 10
        self.treeview = ttk.Treeview(self.Frame_Top, columns=("Test", "Treatment", "Batch", "Path"), show="headings", height=self.treeview_height)
        self.treeview.column("Test", anchor="center", width=50)
        self.treeview.column("Treatment", anchor="center", width=50)
        self.treeview.column("Batch", anchor="center", width=50)
        self.treeview.column("Path", anchor="w", width=300)
        self.treeview.heading("Test", text="Test")
        self.treeview.heading("Treatment", text="Treatment")
        self.treeview.heading("Batch", text="Batch")
        self.treeview.heading("Path", text="Path")
        self.treeview.pack(fill="x")
        self.treeview.bind("<<TreeviewSelect>>", lambda event: self.video_widgets.select_row(self.treeview))

    def create_widgets(self):

        self.Frame_Top = customtkinter.CTkScrollableFrame(self)
        self.Frame_Top.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.Frame_Mid = customtkinter.CTkFrame(self)
        self.Frame_Mid.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.video_widgets = VideoWidgets(self.Frame_Mid, display_frame=self, PROJECT_DIR = self.PROJECT_DIR)
        self.video_widgets.grid(row=0)

        self.Frame_Bot = customtkinter.CTkFrame(self)
        self.Frame_Bot.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        self.confirm_button = customtkinter.CTkButton(self.Frame_Bot, text="Confirm", command=self.on_confirm_click)
        self.confirm_button.grid(row=0, column=0, padx=20, pady=20)
        self.cancel_button = customtkinter.CTkButton(self.Frame_Bot, text="Cancel", command=self.on_cancel_click)
        self.cancel_button.grid(row=0, column=1, padx=20, pady=20)

    def add_row(self, values):
        self.treeview.insert("", "end", values=values)

        # Update treeview height if the last row is added
        if len(self.treeview.get_children()) >= self.treeview_height-1:
            self.treeview_height += 1
            self.treeview.configure(height=self.treeview_height)


    def remove_row(self):
        selected_items = self.treeview.selection()
        if selected_items:
            for item in selected_items:
                self.treeview.delete(item)
        else:
            tkinter.messagebox.showwarning("Warning", "Please select a row to remove")

    # def on_confirm_click(self):
    #     video_types = {'.mp4', '.avi', '.mkv'}

    #     for item in self.treeview.get_children():
    #         values = self.treeview.item(item)['values']
    #         origin_path = values[-1]
    #         fish_dirs, video_contained_dirs = self.video_widgets.get_output_path()

    #         if video_contained_dirs:
    #             message = "The following directories already have videos inside:\n" + "\n".join(str(d) for d in video_contained_dirs)
    #             message += "\nDo you want to remove those and continue?"
    #             user_response = tkinter.messagebox.askyesnocancel("Confirm", message)

    #             if user_response:
    #                 for video_dir in video_contained_dirs:
    #                     for video_file in video_dir.glob('*'):
    #                         if video_file.suffix.lower() in video_types:
    #                             video_file.unlink()
    #             # if user said No, pass
    #             elif not user_response:
    #                 pass
    #             # if user said Cancel, break
    #             else:
    #                 continue

    #         for fish_dir in fish_dirs:
    #             video_files = [f for f in fish_dir.glob("*") if f.is_file() and f.suffix.lower() in video_types]
    #             if not video_files:
    #                 target_path = fish_dir / Path(origin_path).name
    #                 print(f"Copying to {target_path}")
    #                 shutil.copy(origin_path, target_path)

    #     self.destroy()

    def copy_files_and_update_progress(self, origin_path, output_progress, progress_frame):
        def update_label(path, success):
            if success:
                output_progress[path].set(f"{path}    ✓")
            else:
                output_progress[path].set(f"{path}    ✗")

        for fish_dir in output_progress.keys():
            output_path = Path(fish_dir) / origin_path.name
            try:
                shutil.copy(origin_path, output_path)
                update_label(fish_dir, True)
                progress_frame.update()
            except Exception as e:
                print(e)
                update_label(fish_dir, False)
                progress_frame.update()

    def on_confirm_click(self):
        # Create a Toplevel window for displaying the copying progress
        progress_window = tkinter.Toplevel(self)
        progress_window.title("Copying Progress")
        progress_window.geometry("500x300")

        # Create a Canvas widget with a Scrollbar
        progress_frame = tkinter.Canvas(progress_window)
        progress_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        scrollbar = tkinter.Scrollbar(progress_window, orient=tkinter.VERTICAL, command=progress_frame.yview)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        progress_frame.configure(yscrollcommand=scrollbar.set)
        progress_frame.bind('<Configure>', lambda e: progress_frame.configure(scrollregion=progress_frame.bbox('all')))

        # Create a Frame to hold the labels
        label_frame = tkinter.Frame(progress_frame)
        progress_frame.create_window((0, 0), window=label_frame, anchor=tkinter.NW)


        video_types = {'.mp4', '.avi', '.mkv'}

        output_progress_dict = {}
        row = 0

        for item in self.treeview.get_children():
            
            output_progress = {}

            values = self.treeview.item(item)['values']
            origin_path = Path(values[-1])
            fish_dirs, video_contained_dirs = self.video_widgets.get_output_path(test=values[0], treatment=values[1], batch=values[2])

            print("Dealing with {}".format(origin_path))

            if video_contained_dirs:
                message = "The following directories already have videos inside:\n" + "\n".join(str(d) for d in video_contained_dirs)
                message += "\nPress Yes to Remove those and Continue, No to Skip the current one, Cancel to Stop"
                user_response = tkinter.messagebox.askyesnocancel("Confirm", message)

                if user_response:
                    for video_dir in video_contained_dirs:
                        for video_file in video_dir.glob('*'):
                            if video_file.suffix.lower() in video_types:
                                video_file.unlink()
                # if user said No, pass
                elif not user_response:
                    continue
                # if user said Cancel, break
                else:
                    break

            # Add origin_path label
            origin_label = tkinter.Label(label_frame, text=f"Copying {origin_path.name} to:")
            origin_label.grid(row=row, column=0, sticky='w')
            row += 1

            # Add output_paths labels with progress_var
            for fish_dir in fish_dirs:
                progress_var = tkinter.StringVar()
                progress_var.set(f"{fish_dir}    ...")
                label = tkinter.Label(label_frame, textvariable=progress_var)
                label.grid(row=row, column=0, sticky='w')
                output_progress[str(fish_dir)] = progress_var
                row += 1

            self.copy_files_and_update_progress(origin_path, output_progress, progress_frame)

        # Set the scrollregion of the Canvas widget after adding all the labels
        progress_frame.configure(scrollregion=progress_frame.bbox('all'))

        progress_window.protocol("WM_DELETE_WINDOW", progress_window.destroy)


    def on_cancel_click(self):
        self.destroy()


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Main App")

        button = customtkinter.CTkButton(self, text="Open VideoAdd", command=self.open_video_add)
        button.pack()

    def open_video_add(self):
        video_add_window = VideoAdd(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()