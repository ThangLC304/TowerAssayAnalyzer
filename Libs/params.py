import json
import os
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


def kinda_integer(x):
    if x - round(x, 0) == 0:
        return True
    else:
        return False
    

class TestParams():
    def __init__(self, param_path):

        self.param_path = param_path
        self.params = self.load_params()

        self.common_keys, self.dict_keys = self.classifier()

        self.all_OK, self.errors = self.status_checker()

        if not self.all_OK:
            logger.error(f"Params in {self.param_path} are not all OK")

    def update(self):
        self.params = self.load_params()
        self.all_OK, self.errors = self.status_checker()

    def classifier(self):
        with open(self.param_path) as f:
            params = json.load(f)
        
        common_keys = []
        dict_keys = []

        for key, value in params.items():
            if isinstance(value, dict):
                dict_keys.append(key)
            else:
                common_keys.append(key)

        return common_keys, dict_keys
    
    def status_checker(self):
        statuses = {}
        for key in self.common_keys:
            if self.params[key] == None:
                statuses[key] = "Blank"
            elif key != "CONVERSION RATE" and kinda_integer(self.params[key]) == False:
                statuses[key] = "Not Integer"
            else:
                statuses[key] = "OK"

        # check if number of fishes inside self.params[self.dict_keys] are all the same
        if len(self.dict_keys) > 0:
            fish_num = len(self.params[self.dict_keys[0]])
            for key in self.dict_keys:
                if len(self.params[key]) != fish_num:
                    statuses[key] = "Not Equal"
                else:
                    statuses[key] = "OK"
        
        #if all statuses are OK, return True
        if all([status == "OK" for status in statuses.values()]):
            return True, {}
        else:
            # remove the OK statuses
            statuses = {key: value for key, value in statuses.items() if value != "OK"}
            return False, statuses
            

    def get_fish_num(self):
        self.update()
        if "Not Equal" in self.errors.values():
            logger.error(f"In {self.param_path}, fish numbers are not equal")
            return 0
        else:
            return len(self.params[self.dict_keys[0]])

    def delete_last_fish(self):
        for key in self.dict_keys:
            self.params[key].pop()
        self.save_params()

    def add_fish(self):
        # curent fish number
        fish_num = self.get_fish_num()
        for key in self.dict_keys:
            self.params[key][f"{fish_num+1}"] = self.params[key][f"{fish_num}"]   
        self.save_params()

    def load_params(self):
        with open(self.param_path) as f:
            params = json.load(f)
        return params
    
    def save_params(self):
        with open(self.param_path, 'w') as f:
            json.dump(self.params, f, indent=4)