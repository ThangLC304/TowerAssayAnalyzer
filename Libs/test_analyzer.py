import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
import json
from statistics import mean
from general import *

class Basic(Loader):
    def __init__(self):
        super().__init__(testtype='mirror')


distance_list1 = [1, 2, 3, 4]
distance_list2 = [5, 6, 7, 8]

load = Loader(testtype='mirror')

A = Distance(distance_list1, load.hyp)
B = Distance(distance_list2, load.hyp)

C = A + B
print(C)