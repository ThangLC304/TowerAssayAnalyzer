import logging
from pathlib import Path
import os
import json

# Get a logger
logger = logging.getLogger(__name__)

ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

HISTORY_PATH = Path(ROOT_PATH).parent / "History" / "projects.json"


class TREATMENT_DETAIL():
    def __init__(self, batch_detail, treatment_num):
        treatment_name = f"Treatment {treatment_num}"

        treatment_detail = batch_detail[treatment_name]

        self.substance = treatment_detail[0]
        self.concentration = treatment_detail[1]
        self.concentration_unit = treatment_detail[2]
        self.quantity = treatment_detail[3]
        self.note = treatment_detail[4]


class BATCH_DETAIL():
    def __init__(self, project_detail, batch_num):
        batch_name = f"Batch {batch_num}"

        self.batch_detail = project_detail[batch_name]

    def treatment(self, treatment_num):
        return TREATMENT_DETAIL(self.batch_detail, treatment_num)


class PROJECT_DIR():
    def __init__(self, project_name):
        
        self.project_name = project_name

        self.JSON_INFO = self.loader()

    def loader(self):
        with open(HISTORY_PATH, "r") as f:
            all_projects = json.load(f)

        return all_projects

    def saver(self):
        with open(HISTORY_PATH, "w") as f:
            json.dump(self.JSON_INFO, f, indent = 4)

    def get_dir_path(self):
        return Path(self.JSON_INFO[self.project_name]["DIRECTORY"])

    def add_blank_folders(self, batch_num, treatment_num, target_amount):
        project_path = self.get_dir_path()

        # find children directory of project_path
        test_dirs = [child for child in project_path.iterdir() if child.is_dir()]

        batch_ordinal = ORDINALS[batch_num - 1]

        for test_dir in test_dirs:
            # treatment_dir pattern = "A - Control (1st Batch)"
            treatment_dir = test_dir.glob(f"*{treatment_num}*({batch_ordinal} Batch)")
            treatment_dir = list(treatment_dir)[0]

            # find number of directories inside treatment_dir
            current_fish_list = [child for child in treatment_dir.iterdir() if child.is_dir()]
            current_fish_list = [int(fish.split("_")[0].strip()) for fish in current_fish_list]
            max_fish_num = max(current_fish_list)
            if max_fish_num < target_amount:
                for i in range(max_fish_num + 1, target_amount + 1):
                    new_fish_dir = treatment_dir / f"{i}"
                    new_fish_dir.mkdir()



    def add_fish(self, batch_num, treatment_num, add_amount=1, modify_history=False):
        project_detail = self.JSON_INFO[self.project_name]

        batch_name = f"Batch {batch_num}"
        treatment_name = f"Treatment {treatment_num}"

        if batch_name not in project_detail.keys():
            ERROR = f"Batch {batch_num} does not exist in project {self.project_name}"
            logger.warning(ERROR)
            return ERROR
        
        if treatment_name not in project_detail[batch_name].keys():
            ERROR = f"Treatment {treatment_num} does not exist in batch {batch_num}"
            logger.warning(ERROR)
            return ERROR
        
        # treatment_detail pattern
        # [
        #         "Melamine",
        #         10.0,
        #         "ppm",
        #         10, # fish num
        #         ""
        #     ]
        # Position of fish num in treatment detail
        DATA_NO = 3

        if DATA_NO > len(project_detail[batch_name][treatment_name]):
            ERROR = f"{DATA_NO} out-of-range for {treatment_num}"
            logger.warning(ERROR)
            return ERROR
        
        add_amount = int(add_amount)
        current_fish_num = int(self.JSON_INFO[self.project_name][batch_name][treatment_name][DATA_NO])
        target_fish_num = current_fish_num + add_amount

        if modify_history:
            self.JSON_INFO[self.project_name][batch_name][treatment_name][DATA_NO] = target_fish_num
            self.saver()

        # Add blank folder to project directory
        self.add_blank_folders(batch_num, treatment_num, target_fish_num)


