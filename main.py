import tkinter as tk
from tkinter import filedialog

import os
from pathlib import Path



ROOT = os.path.dirname(os.path.realpath(__file__))



def create_input_box(display_text, location, position, default_value):
    label = tk.Label(location, text=display_text)
    label.grid(row=position, column=0, padx=10, pady=10)
    widget = tk.Entry(location)
    widget.grid(row=position, column=1, padx=10, pady=10)
    widget.insert(0, default_value)
    return widget

conversion_rate_widget = create_input_box('Conversion Rate (cm/pixel):', window, 0, params['CONVERSION_RATE'])
center_x_widget = create_input_box('Center X (pixel):', window, 1, params['CENTER_X'])
center_y_widget = create_input_box('Center Y (pixel):', window, 2, params['CENTER_Y'])
fps_widget = create_input_box('FPS:', window, 3, params['FPS'])
duration_widget = create_input_box('Duration (s):', window, 4, params['DURATION'])
ec_threshold_widget = create_input_box('EC Threshold (pixel):', window, 5, params['EC_THRESHOLD'])
speed_threshold_1_widget = create_input_box('Speed Threshold 1 (cm/s):', window, 6, params['SPEED_THRESHOLD_1'])
speed_threshold_2_widget = create_input_box('Speed Threshold 2 (cm/s):', window, 7, params['SPEED_THRESHOLD_2'])
interaction_threshold_widget = create_input_box('Interaction Threshold (pixel):', window, 8, params['INTERACTION_THRESHOLD'])
fighting_threshold_widget = create_input_box('Fighting Threshold (pixel):', window, 9, params['FIGHTING_THRESHOLD'])
chasing_threshold_widget = create_input_box('Chasing Threshold (pixel):', window, 10, params['CHASING_THRESHOLD'])
