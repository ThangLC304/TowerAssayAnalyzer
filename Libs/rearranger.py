import pandas as pd
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
from misc import *
import json
import argparse
import random
from tqdm import tqdm
import time

class Arranger():
    def __init__(self):
        self.root_dir = self.get_root_dir()
        self.statics = self.read_json()
        self.paths = self.get_paths()

        self.tanks_col = self.statics['tanks_col']
        self.tanks_row = self.statics['tanks_row']

        self.raw_df, self.tanks_list = self.get_raw_df()
        self.tanks_num = len(self.tanks_list)
        
        self.im, video_path = self.get_image(source = 'image')
        self.name = Path(video_path).stem

        self.TL_num = self.tanks_num
        self.TR_num = self.TL_num - self.tanks_col + 1
        self.BL_num = self.tanks_col

        self.tanks_dict_creator()


    def get_root_dir(self):
        return Path(__file__).parent.parent


    def read_json(self):
        json_path = os.path.join(self.root_dir, 'Bin', 'statics.json')
        with open(json_path, 'r') as file:
            data = file.read()
        return json.loads(data)
    

    def get_paths(self):
        paths = {}
        for key, value in self.statics['PATHS'].items():
            paths[key] = os.path.join(self.root_dir, value)

        return paths


    def get_raw_df(self):

        # Open dialog to choose the .txt file
        file_type = [('Text File', '*.txt')]
        default_dir = 'Input'
        txt_path = get_file_path(file_type, default_dir)

        raw_df, tanks_list = load_raw_df(txt_path)
        raw_df, _ = clean_df(raw_df)

        return raw_df, tanks_list
    

    def get_image(self, source = 'video'):

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
    

    def fill_outer_columns(self):

        # fill the left most column of tanks
        x_sep = (self.tanks_dict[self.BL_num][0] - self.tanks_dict[self.TL_num][0])/(self.tanks_row - 1)
        y_sep = (self.tanks_dict[self.BL_num][1] - self.tanks_dict[self.TL_num][1])/(self.tanks_row - 1)
        w_sep = (self.tanks_dict[self.BL_num][2] - self.tanks_dict[self.TL_num][2])/(self.tanks_row - 1)
        h_sep = (self.tanks_dict[self.BL_num][3] - self.tanks_dict[self.TL_num][3])/(self.tanks_row - 1)

        for cell in range(self.BL_num, self.TL_num):
            self.tanks_dict[cell] = (self.tanks_dict[self.TL_num] + (self.TL_num - cell)*x_sep, self.tanks_dict[self.TL_num] + (self.TL_num - cell)*y_sep, self.tanks_dict[self.TL_num] + (self.TL_num - cell)*w_sep, self.tanks_dict[self.TL_num] + (self.TL_num - cell)*h_sep)

        # fill the right most column of tanks
        x_sep = (self.tanks_dict[1][0] - self.tanks_dict[self.TR_num][0])/(self.tanks_row - 1)
        y_sep = (self.tanks_dict[1][1] - self.tanks_dict[self.TR_num][1])/(self.tanks_row - 1)
        w_sep = (self.tanks_dict[1][2] - self.tanks_dict[self.TR_num][2])/(self.tanks_row - 1)
        h_sep = (self.tanks_dict[1][3] - self.tanks_dict[self.TR_num][3])/(self.tanks_row - 1)

        for i in range(1, self.TR_num):
            self.tanks_dict[i] = (self.tanks_dict[self.TR_num][0] + x_sep*(self.TR_num-i), self.tanks_dict[self.TR_num][1] + y_sep*(self.TR_num-i), self.tanks_dict[self.TR_num][2] + w_sep*(self.TR_num-i), self.tanks_dict[self.TR_num][3] + h_sep*(self.TR_num-i))


    def fill_row(self, start, end, display = False):

        x_sep = (self.tanks_dict[start][0] - self.tanks_dict[end][0])/(end - start)
        y_sep = (self.tanks_dict[start][1] - self.tanks_dict[end][1])/(end - start)
        w_sep = (self.tanks_dict[start][2] - self.tanks_dict[end][2])/(end - start)
        h_sep = (self.tanks_dict[start][3] - self.tanks_dict[end][3])/(end - start)

        for i in range(start+1, end):
            self.tanks_dict[i] = (self.tanks_dict[end][0] + x_sep*(end-i), self.tanks_dict[end][1] + y_sep*(end-i), self.tanks_dict[end][2] + w_sep*(end-i), self.tanks_dict[end][3] + h_sep*(end-i))
        
        if display:
            for key, value in locals().items():
                print(key + ' = ' + str(value))


    def tanks_dict_creator(self):
        history = self.check_history()
        if history == {}: # No history
            self.tanks_dict_createnew()
        else:
            print("Saved tanks dictionary: \n", history)
            user_input = input('Tanks coordinates history found. Do you want to use it? (y/n)')
            if user_input == 'y':
                self.tanks_dict = history
            elif user_input == 'n':
                self.tanks_dict_createnew()
            else:
                print('Invalid input. Please enter y or n.')
                self.tanks_dict_creator()
                    

    def tanks_dict_createnew(self):
        self.tanks_dict = self.init_tanks_dict()
        self.fill_tanks_dict()
        self.export_tanks_dict()


    def init_tanks_dict(self):

        example_tanks = get_tanks(self.im)
        tanks_dict = {}

        tanks_dict[self.TL_num] = example_tanks['Top Left']
        tanks_dict[self.TR_num] = example_tanks['Top Right']
        tanks_dict[self.BL_num] = example_tanks['Bottom Left']
        tanks_dict[1] = (tanks_dict[6][0] - (tanks_dict[10][0] - tanks_dict[5][0]), tanks_dict[6][1] - (tanks_dict[10][1] - tanks_dict[5][1]), tanks_dict[6][2]*(tanks_dict[5][2]/tanks_dict[10][2]), tanks_dict[6][3]*(tanks_dict[5][3]/tanks_dict[10][3]))

        return tanks_dict


    def fill_tanks_dict(self):
        
        if self.tanks_row > 2:
            self.fill_outer_columns()

        for row in range(0, self.tanks_row):
            self.fill_row(1 + row * self.tanks_col, (row + 1) * self.tanks_col)

        # round up all the values in tanks_dict to integers
        for key in self.tanks_dict:
            self.tanks_dict[key] = tuple([int(round(i)) for i in self.tanks_dict[key]])


    def check_history(self):
        history_dir = self.paths["HISTORY"]
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        history_path = os.path.join(history_dir, self.name)
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                tanks_dict = json.load(f)
            # convert all keys to integers
            tanks_dict = {int(k): v for k, v in tanks_dict.items()}
        else:
            tanks_dict = {}
        return tanks_dict


    def export_tanks_dict(self):
        file_name = self.name
        history_path = self.paths["HISTORY"]
        output_path = os.path.join(history_path, file_name)
        if not os.path.exists(history_path):
            os.makedirs(history_path)
        if os.path.exists(output_path):
            user_input = input('Tanks coordinates history already exists. Do you want to overwrite it? (y/n)')
            if user_input == 'y':
                pass
            elif user_input == 'n':
                new_name = try_new_name(history_path, file_name)
                output_path = os.path.join(history_path, new_name)
            else:
                print('Invalid input. Please enter y or n.')
                self.export_tanks_dict(file_name)

        with open(output_path, 'w') as f:
            json.dump(self.tanks_dict, f)
        

    def predict_tanks(self, target = 'all'):
        display_img = self.im.copy()

        if target == 'all':
            display_tanks = range(1, 11)
        else:
            display_tanks = list(target)

        for i in display_tanks:
            x, y, w, h = self.tanks_dict[i]
            cv2.rectangle(display_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(display_img, str(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.imshow('Tanks', display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def arrange(self, input_df = pd.DataFrame(), tracking = False, fill = True):
        # if input_df is empty, use self.raw_df
        if input_df.empty:
            input_df = self.raw_df
        print(f'Rearranging... Please wait...')

        columns = input_df.columns

        result_df = pd.DataFrame(columns = columns)
        # use tqdm to show progress bar of the loop
        for idx, row in tqdm(input_df.iterrows(), total = input_df.shape[0]):
            for tank_num in self.tanks_list:
                x = row['X' + str(tank_num)]
                y = row['Y' + str(tank_num)]
                
                # if any of x or y is nan, skip this row
                if np.isnan(x) or np.isnan(y):
                    continue
                tank = in_which_tank(x, y, self.tanks_dict)

                if tank != -1:
                    result_df.loc[idx, 'X' + str(tank)] = x
                    result_df.loc[idx, 'Y' + str(tank)] = y
           

        # Check if result_df has nan values
        result_df, filled_history = clean_df(result_df, fill = fill)

        return result_df, filled_history
    

    def exporter(self, input_df, file_name):
        output_dir = self.paths['OUTPUT']
        input_df.to_csv(os.path.join(output_dir, f'{file_name}.csv'), index = False)
        print('Exported to ' + output_dir + file_name + '.csv')


    def display_arranged(self, display_df, window_name = 'Tanks', mouse = True):
        display_coords(display_df, self.im, window_name = window_name, tanks_list = self.tanks_list, mouse = mouse, tanks_dict = self.tanks_dict)


    # GENERATE RANDOM COORDINATES FOR TEST DATA
    def generate_test_data(self):

        test_dict = {}
        for i in range(1, 11):
            test_dict[i] = coord_generator(self.tanks_dict[i])


        columns = []
        for i in range (1, 11):
            columns.append('x' + str(i))
            columns.append('y' + str(i))

        test_df = pd.DataFrame(columns = columns)
        for i in range(1, 11):
            test_df['x' + str(i)] = [x for x, y in test_dict[i]]
            test_df['y' + str(i)] = [y for x, y in test_dict[i]]

        return test_df
    

    def df_mixer(self, input_df, mix_ratio = 0.3):

        for i in range(2, len(input_df.columns), 2):
            for j in range(0, len(input_df)):
                if random.randint(0, 100) < mix_ratio*100:
                    # swap x 
                    input_df.iloc[j, i], input_df.iloc[j, i-2] = input_df.iloc[j, i-2], input_df.iloc[j, i]
                    # swap y
                    input_df.iloc[j, i+1], input_df.iloc[j, i-1] = input_df.iloc[j, i-1], input_df.iloc[j, i+1]
        
        return input_df


if __name__ == "__main__":

    # take arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type = str, default = None, help = 'test, arrange or debug')
    parser.add_argument('--name', type = str, default = None, help = 'name of the output csv file')
    parser.add_argument('--fill', type = bool, default = True, help = 'fill the missing values or not')

    args = parser.parse_args()

    # test mode
    if args.mode == 'test':
        # initialize the class
        tanks = Arranger()

        # predict tanks
        tanks.predict_tanks()

        # generate test data
        test_df = tanks.generate_test_data()
        tanks.display_arranged(test_df, window_name = 'Generated Test Data')

        # display the mixed test data
        mixed_df = tanks.df_mixer(test_df, 0.3)
        tanks.display_arranged(mixed_df, window_name = 'Mixed-up Test Data')

        # arrange the test data
        arranged_df, _ = tanks.arrange(test_df)

        # display the arranged data
        tanks.display_arranged(arranged_df, window_name = 'Rearranged Mixed-up Test Data')

    # arrange mode if mode == arrage or not specified
    elif args.mode == 'arrange' or args.mode == None:
        # initialize the class
        tanks = Arranger()

        # predict tanks
        tanks.predict_tanks()

        # arrange the test data
        arranged_df, filled_history = tanks.arrange(fill = args.fill)

        print('Exported filled_history to .json file')
        # indent = 4 for pretty print
        json_path = r'C:\Code\ChungyuanProjects\TowerAssayAnalyzer\History\automate_filled_history.json'
        with open(json_path, 'w') as f:
            json.dump(filled_history, f, indent = 4)

        # save the arranged data
        if args.name != None:
            file_name = args.name
            print('Saving as ' + file_name + '.csv')
        else:
            file_name = 'arranged_' + tanks.name
            print('No file name specified. Saving as ' + file_name + '.csv')
        tanks.exporter(arranged_df, file_name)

        # display the arranged data
        tanks.display_arranged(arranged_df)

    # debug mode
    elif args.mode == 'debug':
        # initialize the class
        tanks = Arranger()

        # predict tanks
        tanks.predict_tanks()

        # arrange the test data
        arranged_df, filled_history = tanks.arrange(fill = args.fill)

        # print(filled_history)

        # display the arranged data
        draw_trajectories(arranged_df, tanks.im, tanks.tanks_list, tanks.tanks_dict, filled_history=filled_history)
    

        
