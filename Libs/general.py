import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
import json
from statistics import mean
from word2number import w2n
import re

def ordinal_to_number(ordinal):
    ordinal = ordinal.lower().strip()
    if ordinal[-2:] == "st":
        return w2n(ordinal[:-2])
    elif ordinal[-2:] == "nd":
        return w2n(ordinal[:-2])
    elif ordinal[-2:] == "rd":
        return w2n(ordinal[:-2])
    elif ordinal[-2:] == "th":
        return w2n(ordinal[:-2])
    else:
        return None


ROUND_UP = 4


def dist_cal(x1, y1, x2, y2):

    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_area(x1, y1, x2, y2, x3, y3):

    area = 0.5 * abs(x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))
    return area


def trimmer(df, target_rows, mode):

    cut = len(df) - target_rows

    if mode == 'head':
        df = df.iloc[cut:]
    elif mode == 'tail':
        df = df.iloc[:-cut]
    else:
        raise Exception('mode must be either head or tail')
    return df

#def a function that uppercase first letter of each word in a string
def upper_first(string):
    return ' '.join([word[0].upper() + word[1:] for word in string.split()])


class Loader():
    
    def __init__(self, testtype):

        self.root_dir = self.GetRoot()
        self.statics = self.StaticLoader()
        self.paths = self.PathsLoader()
        self.hyp_path = self.HypPathLoader(testtype)
        self.hyp = self.HypLoader(self.hyp_path)


    def GetRoot(self):

        return Path(__file__).parent.parent
    

    def StaticLoader(self):

        json_path = os.path.join(self.root_dir, 'Bin', 'statics.json')
        with open(json_path, 'r') as file:
            data = file.read()
        return json.loads(data)
    

    def PathsLoader(self):

        paths = {}
        for key, value in self.statics['PATHS'].items():
            paths[key] = os.path.join(self.root_dir, value)
        return paths
    

    def HypPathLoader(self, testtype):

        try:
            hyp_path = os.path.join(self.paths['BIN'], f'hyp_{testtype}.json')
        except FileNotFoundError:
            raise Exception (f'hyp_{testtype}.json file not found')

        return hyp_path


    def HypLoader(self, hyp_path):

        with open(hyp_path, 'r') as file:
            data = json.load(file)
        
        # convert values to int or float
        for key, value in data.items():
            if key == "CONVERSION RATE":
                data[key] = float(value)
            else:
                data[key] = int(value)
        return data
    

    def BasicCalculation(self, input_df):

        # reset index
        input_df = input_df.reset_index(drop=True)
        
        # print('First five row:', input_df[0:5])
        # print('Last five row', input_df[-5:])
        

        calculate_top_position = True

        conversion_rate = self.hyp["CONVERSION RATE"]
        fps = self.hyp["FPS"]
        duration = self.hyp["DURATION"]
        try:
            TBS_line = self.hyp["TOP"]
        except KeyError:
            calculate_top_position = False

        # get names of columns
        cols = input_df.columns

        # Load speed thresholds
        speed_1, speed_2 = self.statics['SPEED_1'], self.statics['SPEED_2']

        # INITIALIZE RESULT DICTIONARY
        output_dict = {}
        units = {}

        # Calculate the distance traveled ( in cm ) each frame
        # Calculate the distance from the center of the tank
        output_dict['distance'] = []  # N-1 points
        units['distance'] = 'cm'

        output_dict['locations'] = []  # N points

        for index, row in input_df.iterrows():
            x1 = input_df.loc[index, cols[0]]
            y1 = input_df.loc[index, cols[1]]

            if index >= len(input_df) -1:
                break

            x2 = input_df.loc[index+1, cols[0]]
            y2 = input_df.loc[index+1, cols[1]]
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / conversion_rate
            output_dict['distance'].append(distance)

            if calculate_top_position:
                # Calculate the location of the fish (top or bottom)
                if x1 < TBS_line:
                    output_dict['locations'].append(1)
                else:
                    output_dict['locations'].append(0)
        # print('Key = distance, length = ', len(output_dict['distance']))
        
        # Calculate the speed ( in cm/s ) each frame
        # N-1 points
        output_dict['speed'] = [x*fps for x in output_dict['distance']]
        units['speed'] = 'cm/s'

        # Calculate the total distance (cm)
        output_dict['total distance'] = sum(output_dict['distance'])
        units['total distance'] = 'cm'

        # Calculate the average speed (cm/s)
        output_dict['average speed'] = mean(output_dict['speed'])
        units['average speed'] = 'cm/s'

        # Count the frames TARGET the speed is in the following range
        # Freezing : < speed_1
        # Swimming : >= speed_1 and < speed_2
        # Rapid movement : >= speed_2

        # Initialize the dict
        output_dict['freezing count'] = 0
        output_dict['swimming count'] = 0
        output_dict['rapid movement count'] = 0

        units['freezing count'] = 'frames'
        units['swimming count'] = 'frames'
        units['rapid movement count'] = 'frames'

        for speed in output_dict['speed']:
            if speed < speed_1:
                output_dict['freezing count'] += 1
            elif speed >= speed_1 and speed < speed_2:
                output_dict['swimming count'] += 1
            else:
                output_dict['rapid movement count'] += 1

        # Calculate the percentage of time spent in each state
        output_dict['freezing percentage'] = output_dict['freezing count'] / len(output_dict['speed']) * 100
        output_dict['swimming percentage'] = output_dict['swimming count'] / len(output_dict['speed']) * 100
        output_dict['rapid movement percentage'] = output_dict['rapid movement count'] / len(output_dict['speed']) * 100

        units['freezing percentage'] = '%'
        units['swimming percentage'] = '%'
        units['rapid movement percentage'] = '%'

        # Calculate time spent in top
        output_dict['percentage time in top'] = sum(output_dict['locations']) / duration * 100
        units['percentage time in top'] = '%'
        output_dict['percentage time in bot'] = 100 - output_dict['percentage time in top']
        units['percentage time in bot'] = '%'

        return output_dict, units
    


    def distance_to(self, df, TARGET, axis = 'Y'):

        assert axis in ['X', 'Y'], 'axis must be X or Y'

        try:
            _ = self.hyp[TARGET]
        except KeyError:
            raise Exception(f'{TARGET} is not defined in this test type')
        
        cols = df.columns
        col_num = 0 if axis == 'X' else 1
        distance_list = []

        for idx, row in df.iterrows():
            distance = abs(row[cols[col_num]] - self.hyp[TARGET])/self.hyp['CONVERSION RATE']
            distance_list.append(distance)

        return Distance(distance_list)


    def timing(self, df, TARGET, axis = 'X', smaller = True):

        assert axis in ['X', 'Y'], 'axis must be X or Y'

        interaction = [] # N points
        interaction_events = {} # N points

        indicator = 1 if smaller else 0
        col_num = 0 if axis == 'X' else 1
        cols = df.columns

        for _, row in df.iterrows():
            coord = row[cols[col_num]]

            # Calculate the mirror biting
            if coord < self.hyp[TARGET]:
                interaction.append(indicator)
            elif coord > self.hyp[TARGET]:
                interaction.append(1-indicator)
            else:
                if smaller:
                    interaction.append(1-indicator)
                else:
                    interaction.append(indicator)

        for i in range(len(interaction)):
            if i == 0:
                if interaction[i] == 1:
                    start_point = i
                continue
            if interaction[i] == 1 and interaction[i-1] == 0:
                start_point = i
            elif interaction[i] == 0 and interaction[i-1] == 1:
                end_point = i
                interaction_events[(start_point, end_point-1)] = end_point - start_point

        # Convert values in mirror_biting_events to seconds
        interaction_events = {k: v/self.hyp["FPS"] for k, v in interaction_events.items()}

        # print('Number of interaction events:', len(interaction_events))
        if len(df) > 0 and len(interaction_events) == 0:
            interaction_events['-1'] = '-1'

        return Time(interaction), Events(interaction_events, self.hyp["DURATION"])


class CustomDisplay():

    def __init__(self):

        pass

    def get_variables(self, magic = False):

        self_dir = [x for x in dir(self) if x not in dir(CustomDisplay)]
        if magic:
            return self_dir
        else:
            return [x for x in self_dir if not x.startswith('__')]

    def __str__(self):

        message = "Variables:\n"
        for variable in self.get_variables():
            message += f'{str(variable)}: {str(getattr(self, variable))}\n'

        return message


class Time(CustomDisplay):

    def __init__(self, time_list):

        self.list = time_list
        self.duration = sum(self.list)
        # print(f'Duration: {self.duration} / {len(self.list)}')
        self.percentage = self.duration / len(self.list) * 100
        self.not_duration = len(self.list) - self.duration
        self.not_percentage = 100 - self.percentage
        self.unit = 's'

    

class Events(CustomDisplay):

    def __init__(self, event_dict, duration):

        self.dict = event_dict

        if '-1' in event_dict.keys():
            self.count = 0
            self.longest = 0
            self.percentage = 0
        else:
            self.count = len(self.dict)
            self.longest = max(self.dict.values())
            self.percentage = self.longest / duration * 100

        self.unit = 's'



class Area(CustomDisplay):

    def __init__(self, area_list):

        self.list = area_list
        self.avg = round(mean(self.list), ROUND_UP)
        self.unit = 'cm^2'
    

    def __add__(self, other):

        temp_list = self.list + other.list
        return Area(temp_list, self.hyp)
    


class Distance(CustomDisplay):

    def __init__(self, distance_list):

        self.list = distance_list
        self.total = round(sum(self.list), ROUND_UP)
        self.avg = round(mean(self.list), ROUND_UP)
        self.unit = 'cm'


    def __add__(self, other):

        temp_list = self.list + other.list
        return Distance(temp_list, self.hyp)
    


class Speed(CustomDisplay):

    def __init__(self, speed_list):

        self.list = speed_list
        self.max = round(max(self.list), ROUND_UP)
        self.min = round(min(self.list), ROUND_UP)
        self.avg = round(mean(self.list), ROUND_UP)
        self.unit = 'cm/s'

    
    def __add__(self, other):

        temp_list = self.list + other.list
        return Speed(temp_list, self.hyp)
    



    



