import tkinter as tk
from tkinter import filedialog
import cv2
from pathlib import Path
import math
import random
import json
import pandas as pd
import os
import openpyxl
import re
from tqdm import tqdm
import numpy as np

def fill_space_in_name():
    root = tk.Tk()
    root.withdraw()
    file_type = [('Any', '*.*')]
    default_dir = 'Input'
    file_paths = filedialog.askopenfilenames(filetypes=file_type, initialdir=default_dir)
    for file_path in file_paths:
        file_path = Path(file_path)
        file_name = file_path.stem
        file_name = file_name.replace(' ', '_')
        file_name = file_name + file_path.suffix
        file_path.rename(file_path.parent / file_name)
    
    print('Done')


def get_file_path(type, initialdir, mode = 'single'):
    root = tk.Tk()
    root.withdraw()
    file_type = type
    default_dir = initialdir
    if mode == 'single':
        file_path = filedialog.askopenfilename(filetypes=file_type, initialdir=default_dir)
        return file_path
    if mode == 'multiple':
        file_paths = filedialog.askopenfilenames(filetypes=file_type, initialdir=default_dir)
        return file_paths

def load_raw_df(txt_path, sep = "\t"):
    # Read the .txt file into a dataframe
    raw_df = pd.read_csv(txt_path, sep = sep)

    # Remove unnecessary columns
    tanks_list = []
    for col in raw_df.columns:
        if "unnamed" in col.lower() or "prob" in col.lower():
            raw_df.drop(col, axis=1, inplace=True)
        if "x" in col.lower():
            # find the number in the column name
            tank_num = re.findall(r'\d+', col)
            tank_num = int(tank_num[0])
            tanks_list.append(tank_num)
    return raw_df, tanks_list

def get_image(source = 'video'):

        if source == 'video':
            # Open dialog to choose the .mp4 file
            file_type = [('Video File', '*.mp4')]
            default_dir = 'Input'
            media_path = get_file_path(file_type, default_dir)

            im = get_thumbnail(media_path)
        
        if source == 'image':
            file_type = [('Image File', '*.png')]
            default_dir = 'Input'
            media_path = get_file_path(file_type, default_dir)

            im = cv2.imread(media_path)

        return im, media_path

def get_thumbnail(video_path):
    video_P = Path(video_path)
    cap = cv2.VideoCapture(video_path)
    _, frame = cap.read()
    cap.release()

    # Export frame as a .png file
    image_P = video_P.parent / (video_P.stem + ".png")
    cv2.imwrite(str(image_P), frame)

    im = cv2.imread(str(image_P))
    return im

def get_tanks(im, tank_names = ['Top Left', 'Top Right', 'Bottom Left']):
    example_tanks = {}

    def tank_selector(im, tank_name):
        while True:
            selected_pixel = cv2.selectROI('Selecting tank at position'+str(tank_name), im)
            
            # print out the coordinates of top left and bottom right pixel of the ROI
            print('Tank at position: ', tank_name)
            print('Top left pixel: x = {}, y = {}'.format(selected_pixel[0], selected_pixel[1]))
            print('Bottom right pixel: x = {}, y = {}'.format(selected_pixel[0] + selected_pixel[2], selected_pixel[1] + selected_pixel[3]))
            print('Middle line: y = {}'.format(selected_pixel[1] + selected_pixel[3] / 2))
            tank_d = math.ceil((selected_pixel[2] + selected_pixel[3]) / 2)
            print('Diameter of the tank : ', tank_d)
            print()
            example_tanks[tank_name] = selected_pixel
            cv2.destroyAllWindows()
            break

    for name in tank_names:
        tank_selector(im, name)

    return example_tanks


def color_generator(color_num):

    color_dict = {}
    for i in range(1, color_num + 1):
        color_dict[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    return color_dict

def color_code_loader():
    return {1: [110, 57, 16], 2: [238, 236, 124], 3: [46, 132, 169], 4: [188, 78, 189], 5: [225, 64, 151], 6: [112, 212, 38], 7: [233, 62, 246], 8: [138, 108, 5], 9: [57, 104, 67], 10: [200, 103, 211]}



def draw_points(input_df, image, tank_number, radius = 2, filled_points = [], draw_nan = False, color_rule = 'tank'):
    assert color_rule in ['tank', 'input'], "color_rule must be either 'tank' or 'input'"    
    # color_dict = color_generator(10)
    color_dict = color_code_loader() 

    # color changes based on tank_number
    if color_rule == 'tank':
        color = color_dict[tank_number]
    for i in range(len(input_df)):
        x = input_df['X' + str(tank_number)][i]
        y = input_df['Y' + str(tank_number)][i]
        # change value type to int, if float round to int
        try:
            x = int(x)
        except:
            if draw_nan == False:
                raise ValueError(f"Value x {x} has type {type(x)}")
            else:
                return image
        try:
            y = int(y)
        except:
            if draw_nan == False:
                raise ValueError(f"Value y {y} has type {type(y)}")
            else:
                return image
        if filled_points == []:
            cv2.circle(image, (x, y), radius, color, -1)
        else:
            # if i in filled_points values, change color to black
            if i in filled_points:
                cv2.circle(image, (x, y), radius, (0, 0, 0), -1)
            else:
                cv2.circle(image, (x, y), radius, color, -1)

    return image


def display_coords(input_df, image, window_name, tanks_list, mouse = True, tanks_dict = {}, wait = 0, filled_history = {}, draw_nan = False):

    im = image.copy()

    if filled_history == {}:
        for i in tanks_list:  
            im = draw_points(input_df, im, i, draw_nan = draw_nan)
    else:
        filled_points = {}
        for key in filled_history.keys():
            filled_points[int(key[-1])] = []
        for key, value in filled_history.items():
            if len(value) == 0:
                continue
            else:
                for k, v in value.items():
                    filled_points[int(key[-1])].append(v)

        print(filled_points)
        
        for i in tanks_list:
            im = draw_points(input_df, im, i, filled_points = filled_points[i])

    # display coordinates when mouse hover over the image
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            if tanks_dict == {}:
                print('x = {}, y = {}'.format(x, y))
                print()
            else:
                print('Tank {}: x = {}, y = {}'.format(in_which_tank(x, y, tanks_dict), x, y))
                print()
    
    # initial window name
    cv2.namedWindow(window_name)
    # set mouse callback function for window
    cv2.imshow(window_name, im)

    if mouse:
        cv2.setMouseCallback(window_name, mouse_callback, param = tanks_list)

    if wait == 0:
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def in_box(input_x, input_y, box):
    x, y, w, h = box
    return x <= input_x <= x + w and y <= input_y <= y + h
    

def in_which_tank(x, y, tanks_dict):
    for tank_num, tank_box in tanks_dict.items():
        if in_box(x, y, tank_box):
            return tank_num
    return -1


def coord_generator(box, points = 1000):
    x, y, w, h = box
    coords = []
    for i in range(points):
        x_coord = random.randint(x, x+w)
        y_coord = random.randint(y, y+h)
        coords.append((x_coord, y_coord))
    return coords


def mix_up(input_dict, mix_ratio = 0.3):
    # input_dict has 10 keys 
    # keys are 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    # values are coordinates inside the tanks
    # mix_ratio is the ratio of mixing up the coordinates
    # mix_ratio = 0.3 means 30% of the coordinates will be mixed up

    for i in range(1, len(input_dict)+1):
        if i == 1:
            continue
        else:
            for j in range(1, len(input_dict[i])+1):
                if random.random() < mix_ratio:
                    # swap the coordinates
                    input_dict[i][j-1], input_dict[i-1][j-1] = input_dict[i-1][j-1], input_dict[i][j-1]
    return input_dict


def try_new_name(directory_path, ori_name):
    parent_path = Path(directory_path)
    # json files in parent_path
    json_files = list(parent_path.glob('*.json'))
    sfx = 1
    new_name = ori_name.stem + '_' + str(sfx) + ori_name.suffix
    while True:
        if new_name in json_files:
            sfx += 1
            new_name = ori_name.stem + '_' + str(sfx) + ori_name.suffix
        else:
            break

    return new_name

def load_threshold(threshold_path, *args):
    # load threshold from a json file
    with open(threshold_path, 'r') as f:
        threshold = json.load(f)

    # convert all values to int
    for key, value in threshold.items():
        threshold[key] = int(value)

    return_result = []
    for arg in args:
        if arg not in threshold:
            raise ValueError(f"{arg} is not in the threshold file")
        else:
            return_result.append(threshold[arg])    

    return return_result

def remove_first_row_if_nan(input_df):
    # if the first row of the dataframe has nan values, remove the entire first row
    while True:
        row_0 = input_df.iloc[0, :]
        if row_0.isnull().values.any():
            input_df = input_df.iloc[1:, :]
            # reset index
            input_df = input_df.reset_index(drop=True)
        else:
            break
    return input_df


def split_array(my_array, sep = 1):
    # get the difference between each number
    diff = np.diff(my_array)
    # get the index of the difference that is larger than sep
    split_index = np.where(diff > sep)[0]
    # split the array into groups
    split_array = np.split(my_array, split_index + 1)
    return split_array



def clean_df(input_df, fill = False, frames = 0, DEBUG = False): 

    # Remove the initial rows with nan values
    input_df = remove_first_row_if_nan(input_df)

    # Only take the first frames rows
    if frames == 0:
        pass
    else:
        input_df = input_df.iloc[:frames, :]


    filled_history = {} # {[filled_value]: [nan_coords]}
    if fill == True:
        # fill nan values with the previous value
        for col in input_df.columns:
            # initialize the filled_history of each column
            filled_history[col] = {}

            if DEBUG:
                print('In column: ', col, '...')
            # find the nan values
            nan_coords = np.where(input_df[col].isnull())[0]    # e.g. array([3, 5], dtype=int64)
            if DEBUG:
                print('Current NaN coordinates: ', nan_coords)
            # if there are nan values
            if len(nan_coords) == 0:
                continue
            
            # split nan_coords into groups of continuous numbers (sep = 1)
            nan_coords_groups = split_array(nan_coords)

            for nan_coords_group in nan_coords_groups:
                # find the previous value
                prev_value = input_df[col][nan_coords_group[0] - 1]
                # # fill the nan values with the previous value
                # input_df[col][nan_coords_group] = prev_value
                # record the filled values
                if prev_value not in filled_history:
                    filled_history[col][prev_value] = nan_coords_group
                else:
                    filled_history[col][prev_value] = np.concatenate((filled_history[col][prev_value], nan_coords_group))
                # change the value in filled_history from np.array to list
                filled_history[col][prev_value] = filled_history[col][prev_value].tolist()
        
        # fill the nan values with the previous value
        input_df = input_df.fillna(method='ffill')

    return input_df, filled_history


def append_df_to_excel(filename, df, sheet_name='Sheet1', startcol=None, startrow=None, col_sep = 0, row_sep = 0,
                       truncate_sheet=False, DISPLAY = False,
                       **to_excel_kwargs):
    # Excel file doesn't exist - saving and exiting
    if not os.path.isfile(filename):
        df.to_excel(
            filename,
            sheet_name=sheet_name, 
            startcol=startcol if startcol is not None else 0, 
            startrow=startrow if startrow is not None else 0,
            **to_excel_kwargs)
        return
    
    if 'engine' in to_excel_kwargs:
        to_excel_kwargs.pop('engine')

    writer = pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay')

    # try to open an existing workbook
    writer.workbook = openpyxl.load_workbook(filename)

    # get the last col in the existing Excel sheet
    # if it was not specified explicitly
    if startcol is None and sheet_name in writer.workbook.sheetnames:
        startcol = writer.workbook[sheet_name].max_column + col_sep

    if startrow is None and sheet_name in writer.workbook.sheetnames:
        startrow = writer.workbook[sheet_name].max_row + row_sep
    
    if startcol is None:
        startcol = 0

    if startrow is None:
        startrow = 0

    if DISPLAY:
        print('In file: ', os.path.basename(filename))
        print('Appended to column: ', startcol,', row: ', startrow)
    
    # write the dataframe to the existing sheet
    df.to_excel(writer, sheet_name, startcol=startcol, startrow=startrow, **to_excel_kwargs)

    # close workbook
    writer.close()


def draw_prep(mode = 'multiple', im_path = None, txt_path = None, sep = ","):
    assert mode in ['single', 'multiple'], "mode must be either 'single' or 'multiple'"

    if im_path == None:
        im, _ = get_image(source = 'image')
    else:
        im = cv2.imread(im_path)

    if txt_path == None:
        file_type = [('Txt or csv files', '*.txt;*.csv')]
        default_dir = 'Input'
        txt_paths = get_file_path(file_type, default_dir, mode = mode)
    else:
        txt_paths = txt_path

    final_df = pd.DataFrame()
    tanks_list = []
    # loop through all the txt files
    # read df and merge to final_df
    print("Reading data")
    if mode == 'single':
        final_df, _ = load_raw_df(txt_paths, sep = sep)
        for col in final_df.columns:
            if 'x' in col.lower():
                tank_num = int(col.lower().split('x')[1])
                tanks_list.append(tank_num)
    else:
        for txt_path in tqdm(txt_paths):
            txt_stem = Path(txt_path).stem
            tank_num = int(txt_stem.split('_')[1])
            tanks_list.append(tank_num)
            df, _ = load_raw_df(txt_path)
            columns = [f'X{tank_num}', f'Y{tank_num}']
            df.columns = columns
            final_df = pd.concat([final_df, df], axis = 1)


        print("Cleaning data")
        final_df, filled_history = clean_df(final_df, fill = True, frames = 3000)

        print('Exported filled_history to .json file')
        # indent = 4 for pretty print
        json_path = r'D:\Code\TowerAssayAnalyzer\History\manual_filled_history.json'
        with open(json_path, 'w') as f:
            json.dump(filled_history, f, indent = 4)

    print('Tanks list', tanks_list)
    print('Final DF')
    print(final_df)

    return final_df, im, tanks_list

def draw_trajectories(final_df, im, tanks_list, until = 3000, mouse = False, wait = 0, filled_history = {}, draw_nan = False):
    final_df = final_df.iloc[:until, :]
    display_coords(final_df, im, window_name = "Display trajectories", mouse = mouse, tanks_list = tanks_list, wait = wait, filled_history = filled_history, draw_nan = draw_nan)


def open_dir(output_dir):
    os.startfile(output_dir)

def create_messagebox(root, title, output_dir):

    message = f'The summary stats are exported to {output_dir}'
    # pop-up a message to notify that the file has been exported
    messagebox = tk.Toplevel(root)
    messagebox.title(title)
    # flexibly set the size of messagebox
    messagebox.geometry('+{}+{}'.format(root.winfo_x() + 500, root.winfo_y() + 250))
    messagebox.configure(bg="white")
    label = tk.Label(messagebox, text=message, font=('Arial', 16, 'bold'))
    label.grid(row=0, column=0, padx=10, pady=20)
    go_button = tk.Button(messagebox, text='Go to Output directory', font=('Arial', 16, 'bold'), command=lambda: open_dir(output_dir))
    go_button.grid(row=1, column=0, padx=10, pady=20)
    go_button.configure(bg = 'dark green', fg = 'white')
    # change the messagebox size to fit the label
    messagebox.update()
    messagebox.after(3000, messagebox.destroy)