import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
import json
from statistics import mean

from Libs.misc import *



class Test():

    def __init__(self, input_df):

        self.root_dir = self.get_root_dir()
        self.statics = self.read_json()
        self.paths = self.get_paths()
        self.hyp = self.load_hyp()
        self.threshold = self.load_threshold()

        self.df = input_df


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
    

    def load_hyp(self):

        hyp_path = os.path.join(self.paths['BIN'], 'hyperparameters.json')
        with open(hyp_path, 'r') as file:
            data = json.load(file)
        
        # convert values to int or float
        for key, value in data.items():
            if key == "CONVERSION RATE":
                data[key] = float(value)
            else:
                data[key] = int(value)
        return data
    

    def load_threshold(self):

        threshold_path = os.path.join(self.paths['BIN'], 'thresholds.json')
        with open(threshold_path, 'r') as file:
            data = json.load(file)
        
        FLOAT_THRESHOLD = []

        # convert values to int or float
        for key, value in data.items():
            if key in FLOAT_THRESHOLD:
                data[key] = float(value)
            else:
                data[key] = int(value)
        return data
    

    def summarize(self, output_dict, units):

         # Summarize output
        summary_dict = {}
        for key, value in output_dict.items():
            # if value is a single value
            if type(value) == int or type(value) == float:
                try:
                    unit = units[key]
                except:
                    unit = ''
                summary_dict[key] = [value, unit]

        return summary_dict

    
    def BasicCalculation(self):

        conversion_rate = self.hyp["CONVERSION RATE"]
        fps = self.hyp["FPS"]
        duration = self.hyp["DURATION"]

        TBS_line = self.hyp["TOP"]


        # rename the columns from Xn, Yn to X and Y
        self.df = self.df.rename(columns = lambda x : x[0])

        # Load speed thresholds
        speed_1, speed_2 = self.threshold['SPEED_1'], self.threshold['SPEED_2']

        # INITIALIZE RESULT DICTIONARY
        output_dict = {}
        units = {}

        # Calculate the distance traveled ( in cm ) each frame
        # Calculate the distance from the center of the tank
        output_dict['distance'] = []  # N-1 points
        units['distance'] = 'cm'

        for index, row in self.df.iterrows():
            x1 = self.df.loc[index, 'X']
            y1 = self.df.loc[index, 'Y']

            if index != len(self.df) - 1:
                x2 = self.df.loc[index+1, 'X']
                y2 = self.df.loc[index+1, 'Y']
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / conversion_rate
                output_dict['distance'].append(distance)

            # Calculate the location of the fish (top or bottom)
            if x1 < TBS_line:
                output_dict['locations'].append(1)
            else:
                output_dict['locations'].append(0)


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

        # Count the frames where the speed is in the following range
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


class NovelTankTest(Test):
    def __init__(self, input_df):
        super().__init__(input_df)
        self.basic = self.BasicCalculation()
        self.basicinfo = self.summarize(self.basic)

    def calc(self):
        conversion_rate = self.hyp["CONVERSION RATE"]
        fps = self.hyp["FPS"]
        # duration = self.hyp["DURATION"]

        center_line = self.hyp["CENTER"]

        # INITIALIZE RESULT DICTIONARY
        output_dict = {}
        units = {}

        output_dict['distance from center line'] = [] # N points
        units['distance from center line'] = 'cm'

        output_dict['locations'] = [] # N points (top if < TBS_line, bottom if >= TBS_line) (top = 1, bottom = 0)

        output_dict['distance traveled in top'] = 0
        units['distance traveled in top'] = 'cm'

        output_dict['latency to enter the top in (frame)'] = 0
        units['latency to enter the top (frame)'] = 'frames'

        output_dict['latency to enter the top in (seconds)'] = 0
        units['latency to enter the top (seconds)'] = 's'

        # Use some info from basic calculation
        basic_dict, _ = self.basic

        for index, row in self.df.iterrows():
            # x1 = self.df.loc[index, 'X']
            y1 = self.df.loc[index, 'Y']

            # Calculate the distance from the center line of the tank (only Y coordinate)
            distance_from_center_line = abs(y1 - center_line) / conversion_rate
            output_dict['distance from center line'].append(distance_from_center_line)

            # Calculate the distance from the center line of the tank (only Y coordinate)
            distance_from_center_line = abs(y1 - center_line) / conversion_rate
            output_dict['distance from center line'].append(distance_from_center_line)

            # Calculate the location of the fish (top or bottom)
            if basic_dict['location'][index] == 1:
                output_dict['distance traveled in top'] += basic_dict['distance'][index]
                output_dict['latency to enter the top in (frame)'] = index+1

        # Calculate the average distance from the center line of the tank
        output_dict['average distance from center line'] = mean(output_dict['distance from center line'])
        units['average distance from center line'] = 'cm'


        # Calculate percentage of distance traveled in top / distance traveled in total
        output_dict['percentage distance traveled in top'] = output_dict['distance traveled in top'] / basic_dict['total distance'] * 100
        units['percentage distance traveled in top'] = '%'

        # Calculate latency to enter the top in second
        output_dict['latency to enter the top in (seconds)'] = output_dict['latency to enter the top in (frame)'] / fps

        # Calculate the top/bot events
        # Initialize the dict
        output_dict['top entries'] = {}
        for i in range(len(output_dict['locations'])):
            if i == 0:
                if output_dict['locations'][i] == 1:
                    start_point = i
                continue
            if output_dict['locations'][i] == 1 and output_dict['locations'][i-1] == 0:
                start_point = i
            elif output_dict['locations'][i] == 0 and output_dict['locations'][i-1] == 1:
                end_point = i
                output_dict['top entries'][(start_point, end_point-1)] = end_point - start_point  

        # Calculate entries count
        output_dict['top entries count'] = len(output_dict['top entries'])
        units['top entries count'] = 'entries'

        # Calculate average top entry duration per entry
        output_dict['average top entry duration'] = sum(output_dict['locations']) / fps / output_dict['top entries count']
        units['average top entry duration'] = 's'

        return self.summarize(output_dict, units)


class ShoalingTest():

    def __init__(self, input_df1, input_df2, input_df3):

        self.dfs = {}

        self.dfs[1] = input_df1
        self.dfs[2] = input_df2
        self.dfs[3] = input_df3

        self.df1_basic, _ = Test(self.dfs[1]).BasicCalculation()
        self.df2_basic, _ = Test(self.dfs[2]).BasicCalculation()
        self.df3_basic, _ = Test(self.dfs[3]).BasicCalculation()

        self.df_shape_check()


    def df_shape_check(self):

        ORDINAL = ['First', 'Second', 'Third']
        max_length = max(len(self.dfs[1]), len(self.dfs[2]), len(self.dfs[3]))
        for i in range(1, 4):
            if len(self.dfs[i]) < max_length:
                print(f'The {ORDINAL[i-1]} dataframe has less row of values than others: {len(self.dfs[i])} < {max_length}')
                raise Exception
            

    def average_distance(self, dfA, dfB):

        for i in range(len(dfA)):
            pass


class MirrorBitingTest(Test):
    def __init__(self, input_df):
        super().__init__(input_df)
        self.basicinfo = self.BasicCalculation()

    def calc(self):
        # conversion_rate = self.hyp["CONVERSION RATE"]
        fps = self.hyp["FPS"]
        duration = self.hyp["DURATION"]

        mirror = self.hyp["MIRROR"]

        # INITIALIZE RESULT DICTIONARY
        output_dict = {}
        units = {}

        output_dict['mirror biting'] = [] # N points
        units['mirror biting'] = '' # N points, 1 if mirror biting, 0 if not

        output_dict['mirror biting events'] = {} # N points
        units['mirror biting events'] = ''

        for index, _ in self.df.iterrows():
            x1 = self.df.loc[index, 'X']

            # Calculate the mirror biting
            if x1 < mirror:
                output_dict['mirror biting'].append(1)
            else:
                output_dict['mirror biting'].append(0)

        for i in range(output_dict['mirror biting']):
            if i == 0:
                if output_dict['mirror biting'][i] == 1:
                    start_point = i
                continue
            if output_dict['mirror biting'][i] == 1 and output_dict['mirror biting'][i-1] == 0:
                start_point = i
            elif output_dict['mirror biting'][i] == 0 and output_dict['mirror biting'][i-1] == 1:
                end_point = i
                output_dict['mirror biting events'][(start_point, end_point-1)] = end_point - start_point

        # Calculate the mirror biting percentage
        output_dict['mirror biting percentage'] = sum(output_dict['mirror biting']) / fps / duration * 100
        units['mirror biting percentage'] = '%'

        # Calculate longest mirror biting event & its percentage
        try:
            output_dict['longest mirror biting time'] = max(output_dict['interaction events'].values())
        except ValueError:
            output_dict['longest mirror biting time'] = 0
        try:
            output_dict['longest mirror biting percentage'] = output_dict['longest mirror biting time']/len(output_dict['mirror biting'])*100
        except ZeroDivisionError:
            output_dict['longest mirror biting percentage'] = 0

        return self.summarize(output_dict, units)


class SocialInteractionTest(Test):
    pass

class PredatorAvoidanceTest(Test):
    pass
