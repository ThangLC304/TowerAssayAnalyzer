import tkinter as tk
from tkinter import filedialog
import cv2
from pathlib import Path
import math
import random

def get_file_path(type, initialdir):
    root = tk.Tk()
    root.withdraw()
    file_type = type
    default_dir = initialdir
    file_path = filedialog.askopenfilename(filetypes=file_type, initialdir=default_dir)
    return file_path

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


def display_coords(input_df, image, window_name):

    im = image.copy()

    color_dict = color_generator(10)

    def draw_points(input_df, image, tank_number, radius = 2):
        # color changes based on tank_number
        color = color_dict[tank_number]
        for i in range(len(input_df)):
            x = input_df['x' + str(tank_number)][i]
            y = input_df['y' + str(tank_number)][i]
            try:
                cv2.circle(image, (x, y), radius, color, -1)
            except:
                print(f"Value {x} has type {type(x)}")
                print(f"Value {y} has type {type(y)}")
        return image

    for i in range(1, 11):
        im = draw_points(input_df, im, i)
    cv2.imshow(window_name, im)
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