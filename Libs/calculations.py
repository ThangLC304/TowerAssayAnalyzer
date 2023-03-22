import pandas as pd
import math
from statistics import mean
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
THRESHOLD_PATH = ROOT / 'Bin' / 'statics.json'

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

# IN THE VIDEO, THE TOP SIDE OF THE TANK IS ON THE LEFT SIDE OF THE SCREEN, AND THE BOTTOM SIDE OF THE TANK IS ON THE RIGHT SIDE OF THE SCREEN
# HENCE WHEN CONSIDER THE LOCATION OF THE FISH, WE USE THE THRESHOLD OF THE X COORDINATE (top_bot_split_line or TBS_line) TO DETERMINE WHETHER THE FISH IS IN THE TOP OR BOTTOM TANK
# WE MEASURE THE DISTANCE TO THE CENTER LINE (y axis) TO SEE IF THE FISH IS IN THE RECTANGLE AREA IN THE MIDDLE OF THE TANK OR NOT

def BasicCalculation(input_df, conversion_rate, TBS_line, center_line, fps = 50, duration = 60):
    # input_df is a pandas dataframe
    # columns are "Xn" and "Yn" where n is the tank number
    # values in the columns are the coordinates of the fish in the tank at a given frame
    # total of 3000 frames in the video (60 seconds * 50 fps)
    # conversion_rate is the number of pixels per cm

    # rename the columns from Xn, Yn to X and Y
    input_df = input_df.rename(columns = lambda x : x[0])

    # Load speed thresholds
    speed_1, speed_2 = load_threshold(THRESHOLD_PATH, 'SPEED_1', 'SPEED_2')

    # INITIALIZE RESULT DICTIONARY
    output_dict = {}
    units = {}

    # Calculate the distance traveled ( in cm ) each frame
    # Calculate the distance from the center of the tank
    output_dict['distance'] = []  # N-1 points
    units['distance'] = 'cm'

    output_dict['distance from center line'] = [] # N points
    units['distance from center line'] = 'cm'

    output_dict['locations'] = [] # N points (top if < TBS_line, bottom if >= TBS_line) (top = 1, bottom = 0)

    for index, row in input_df.iterrows():
        x1 = input_df.loc[index, 'X']
        y1 = input_df.loc[index, 'Y']

        if index != len(input_df) - 1:
            x2 = input_df.loc[index+1, 'X']
            y2 = input_df.loc[index+1, 'Y']
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / conversion_rate
            output_dict['distance'].append(distance)

        # Calculate the distance from the center line of the tank (only Y coordinate)
        distance_from_center_line = abs(y1 - center_line) / conversion_rate
        output_dict['distance from center line'].append(distance_from_center_line)

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

    # Calculate the average distance from the center line of the tank
    output_dict['average distance from center line'] = mean(output_dict['distance from center line'])
    units['average distance from center line'] = 'cm'

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

    return output_dict, units

def NovelTank(input_df):
    # rename the columns from Xn, Yn to X and Y
    input_df = input_df.rename(columns = lambda x : x[0])

    # Load speed thresholds
    speed_1, speed_2 = load_threshold(THRESHOLD_PATH, 'SPEED_1', 'SPEED_2')

    # INITIALIZE RESULT DICTIONARY
    output_dict = {}
    units = {}

    output_dict['distance from center line'] = [] # N points
    units['distance from center line'] = 'cm'

    output_dict['locations'] = [] # N points (top if < TBS_line, bottom if >= TBS_line) (top = 1, bottom = 0)




