import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
import json
from statistics import mean
from Libs.general import *



ROUND_UP = 4



class NovelTankTest(Loader): # 3000 * 7

    def __init__(self, input_df):

        super().__init__(testtype='noveltank')

        self.df = input_df
        self.cols = self.df.columns
        self.basic, _ = self.BasicCalculation(self.df)

        self.distance = self.distance_to(self.df, "CENTER")
        self.time, self.events = self.timing(self.df, "TOP", "X", smaller = True)

        self.others = {}
        self.others['distance in top'], self.others['top/bottom ratio'] = self.distance_in_top()
        self.others['latency'] = self.latency_calculation()


    def distance_in_top(self):
        
        distance_list = self.distance.list
        in_top_list = self.time.list

        distance_in_top = 0

        for i in range(len(distance_list)):
            if in_top_list[i] == 1:
                distance_in_top += distance_list[i]

        top_bottom_ratio = distance_in_top / self.basic["total distance"]

        return distance_in_top, top_bottom_ratio
    

    def latency_calculation(self):

        latency = 1
        for instance in self.time.list[1:]:
            if instance == 0:
                latency += 1
            else:
                break
        latency = latency / self.hyp["FPS"]

        return latency



### DONE ###
class ShoalingTest(Loader):

    def __init__(self, input_df1, input_df2, input_df3):

        super().__init__(testtype='shoaling')

        self.df = {}

        self.df[1] = input_df1
        self.df[2] = input_df2
        self.df[3] = input_df3

        self.basic[1], _ = self.BasicCalculation(self.df[1])
        self.basic[2], _ = self.BasicCalculation(self.df[2])
        self.basic[3], _ = self.BasicCalculation(self.df[3])

        self.equalize_mode = 'head'
        self.frames = self.df_shape_check()


    def df_shape_check(self):

        ORDINAL = ['First', 'Second', 'Third']

        min_length = min(len(self.df[1]), len(self.df[2]), len(self.df[3]))
        lowest_one = ''

        for i in range(1, 4):
            if len(self.df[i]) == min_length:
                lowest_one = i
            if len(self.df[i]) > min_length:
                print(f'The {ORDINAL[i-1]} dataframe has {len(self.df[i])} rows, more than the lowest one ({ORDINAL[lowest_one-1]}).')
                if self.equalize_mode == 'head':
                    self.df[i] = trimmer(self.df[i], target_rows = min_length, mode = equalize_mode)
        
        return min_length    

    # distance_to_center in general.py    

    def distance_to_other(self, dfA, dfB):

        A_cols = dfA.columns
        B_cols = dfB.columns
        distance_list = []
        for i in range(len(dfA)):
            distance = dist_cal(dfA.loc[i, A_cols[0]], dfA.loc[i, A_cols[1]], dfB.loc[i, B_cols[0]], dfB.loc[i, B_cols[1]])
            distance = distance / self.hyp['CONVERSION RATE']
            distance_list.append(distance)

        return Distance(distance_list)


    def shoal_area(self):

        #Calculate the shoal area per frame
        shoal_area_list = []
        for i in range(len(self.df[1])):
            shoal_area = calculate_area(self.df[1].loc[i, 'X'], self.df[1].loc[i, 'Y'], self.df[2].loc[i, 'X'], self.df[2].loc[i, 'Y'], self.df[3].loc[i, 'X'], self.df[3].loc[i, 'Y'])
            shoal_area = shoal_area / self.hyp['CONVERSION RATE']**2
            shoal_area_list.append(shoal_area)

        return Area(shoal_area_list)


    def distance_filter(self, df_num):

        others = [n for n in range(1, 4) if n != df_num]
        distance_1 = self.average_distance(self.df[df_num], self.df[others[0]]) # converted
        distance_2 = self.average_distance(self.df[df_num], self.df[others[1]]) # converted
        nearest_distance_list = []
        furthest_distance_list = []

        for i in range(len(distance_1)):
            nearest_distance_list.append(min(distance_1[i], distance_2[i]))
            furthest_distance_list.append(max(distance_1[i], distance_2[i]))

        return Distance(nearest_distance_list), Distance(furthest_distance_list)



### DONE ###
class MirrorBitingTest(Loader):

    def __init__(self, input_df):

        super().__init__(testtype='mirror')

        self.df = input_df
        self.cols = self.df.columns
        self.basic, _ = self.BasicCalculation(self.df)

        self.time, self.events = self.timing(self.df, "MIRROR", "Y", smaller = True)

    
    def mirror_timing(self):

        mirror_biting = [] # N points
        mirror_biting_events = {} # N points

        for _, row in self.df.iterrows():
            y = row[self.cols[1]]

            # Calculate the mirror biting
            if y < self.hyp["MIRROR"]:
                mirror_biting.append(1)
            else:
                mirror_biting.append(0)

        for i in range(len(mirror_biting)):
            if i == 0:
                if mirror_biting[i] == 1:
                    start_point = i
                continue
            if mirror_biting[i] == 1 and mirror_biting[i-1] == 0:
                start_point = i
            elif mirror_biting[i] == 0 and mirror_biting[i-1] == 1:
                end_point = i
                mirror_biting_events[(start_point, end_point-1)] = end_point - start_point

        # Convert values in mirror_biting_events to seconds
        mirror_biting_events = {k: v/self.hyp["FPS"] for k, v in mirror_biting_events.items()}

        return Time(mirror_biting), Events(mirror_biting_events, self.hyp["DURATION"])
    


### DONE ###
class SocialInteractionTest(Loader):

    def __init__(self, input_df):

        super().__init__(testtype='social')

        self.df = input_df
        self.cols = self.df.columns
        self.basic, _ = self.BasicCalculation(self.df)

        self.distance = self.distance_to(self.df, "SEPARATOR", "Y")
        self.time, self.events = self.timing(self.df, "CONSPECIFIC", "Y", smaller = False)


    def social_timing(self):

        social_interaction = [] # N points
        social_interaction_events = {} # N points

        for _, row in self.df.iterrows():
            y = row[self.cols[1]]

            # Calculate the social interaction
            if y > self.hyp["CONSPECIFIC"]:
                social_interaction.append(1)
            else:
                social_interaction.append(0)

        for i in range(len(social_interaction)):
            if i == 0:
                if social_interaction[i] == 1:
                    start_point = i
                continue
            if social_interaction[i] == 1 and social_interaction[i-1] == 0:
                start_point = i
            elif social_interaction[i] == 0 and social_interaction[i-1] == 1:
                end_point = i
                social_interaction_events[(start_point, end_point-1)] = end_point - start_point

        # Convert values in social_interaction_events to seconds
        social_interaction_events = {k: v/self.hyp["FPS"] for k, v in social_interaction_events.items()}

        return Time(social_interaction), Events(social_interaction_events, self.hyp["DURATION"])
    

    def distance_to_separator(self):

        distance_list = []

        for _, row in self.df.iterrows():
            y = row[self.cols[1]]
            distance = abs(y - self.hyp["SEPARATOR"])
            distance = distance / self.hyp['CONVERSION RATE']
            distance_list.append(distance)

        return Distance(distance_list)



### DONE ###
class PredatorAvoidanceTest(Loader):
    
    def __init__(self, input_df):

        super().__init__(testtype='predator')

        self.df = input_df
        self.cols = self.df.columns
        self.basic, _ = self.BasicCalculation(self.df)

        self.distance = self.distance_to(self.df, "SEPARATOR", "Y")
        self.time, self.events = self.timing(self.df, "PREDATOR", "Y", smaller = True)


    def distance_to_separator(self):

        distance_list = []

        for _, row in self.df.iterrows():
            y = row[self.cols[1]]
            distance = abs(y - self.hyp["SEPARATOR"])
            distance = distance / self.hyp['CONVERSION RATE']
            distance_list.append(distance)

        return Distance(distance_list)