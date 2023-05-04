from pathlib import Path
from Libs.executor import *
from Libs.misc import sort_paths_by_parent, hyploader
import pandas as pd
import json
import time
from tqdm import tqdm

tests = ['Novel Tank', 'Shoaling', 'Mirror Biting', 'Social Interaction', 'Predator Avoidance']
keywords = [x.split(' ')[0].lower() for x in tests]
test_execs = [noveltank_exec, shoaling_exec, mirrorbiting_exec, socialinteraction_exec, predatoravoidance_exec]

class MY_CONDITION():

    def __init__(self, test_name, condition, condition_path, no_gap, hyp):
        
        self.test_name = test_name

        self.condition = condition

        self.no_gap = no_gap

        self.hyp = hyp

        self.trajectory_format = self.set_trajectory_type()

        self.targets = self.find_targets(condition_path)
     

    def find_targets(self, condition_path):
        
        trajectories = condition_path.glob(f'**/{self.trajectory_format}')
        trajectories = sort_paths_by_parent(trajectories)
        targets = {trajectory.parent.name: trajectory for trajectory in trajectories}
        targets = self.priotize_data(targets, mode = 'last')
        
        return targets



    def priotize_data(self, input_dict, mode = 'last'):
        
        key_group = {}
        for key in input_dict.keys():
            k = key.split('-')[0].strip()
            if k not in key_group:
                key_group[k] = [key]
            else:
                key_group[k].append(key)

        def sub_num(input_str):
            return int(input_str.split('-')[1].strip())


        for k, v in key_group.items():
            remove_list = []
            if len(v) > 1:
                addition_list = [x for x in v if x != k]
                if mode == 'first':
                    remove_list = addition_list
                elif mode == 'last':
                    last_num = max([sub_num(x) for x in addition_list])
                    remove_list = [x for x in addition_list if sub_num(x) != last_num]
                    remove_list.append(k)
                else:
                    try:
                        chosen = int(mode)
                        if chosen in [sub_num(x) for x in addition_list]:
                            remove_list = [x for x in addition_list if sub_num(x) != chosen]
                            remove_list.append(k)
                    except:
                        raise ValueError('mode must be first or last or an integer')
                    
            # print(remove_list)
            for key in remove_list:
                input_dict.pop(key)
        
        return input_dict



    def set_trajectory_type(self):

        if self.no_gap:
            trajectory_format = "trajectories_nogaps.txt"
        else:
            trajectory_format = "trajectories.txt"

        return trajectory_format
    

    def analyze(self, target_name, seg_num = 1):

        if self.test_name not in tests:
            raise ValueError(f'{self.test_name} is not a valid test name')
        
        test_index = tests.index(self.test_name)
        # print('Running test: ', self.test_name, '...')
        test_exec = test_execs[test_index]

        for target, target_path in self.targets.items():
            # print(f'Scanning {target} if == {target_name}', end = '...')
            if target == target_name:
                # print(' Matched !', end = '\n')
                if test_index == 0:
                    results = test_exec(target_path, project_hyp = self.hyp, seg_num = seg_num)
                    # test_exec("1", "../PROJECT/{num} - Test/{char} - Treatment ({ordinal} Batch)/{target}/.txt")
                else:
                    results = test_exec(target_path, project_hyp = self.hyp)
                return results # in format [key, value], not {key: value} for easy retrieval


    def info(self):

        output_text = f'In condition {self.condition}, we have: \n'
        for target, target_path in self.targets.items():
            output_text += f'Fish group {target} : {target_path} \n'

        print(output_text)





class MY_BATCH():

    def __init__(self, test_name, batch_num, batch_paths, no_gap, hyp):

        self.test_name = test_name


        self.num = batch_num

        self.conditions = self.extract_conditions(batch_paths)

        self.hyp = hyp

        self.condition = {}
        for condition, cond_path in self.conditions.items():
            self.condition[condition] = MY_CONDITION(test_name = self.test_name, 
                                                     condition = condition, 
                                                     condition_path = cond_path, 
                                                     no_gap = no_gap, 
                                                     hyp = self.hyp)

    def extract_conditions(self, batch_paths):

        def get_name(pathlib_path):

            name = pathlib_path.name.split('-')[0]
            name = name.strip()

            return name

        conditions = {}
        for batch_path in batch_paths:
            conditions[get_name(batch_path)] = batch_path

        return conditions


    def info(self):

        output_text = f"In Batch {self.num}, we have: \n"
        for condition, cond_path in self.conditions.items():
            output_text += f"Condition {condition} : {cond_path} \n"
        
        print(output_text)




class MY_DIR():

    def __init__(self, name, dir_path, no_gap = False):

        project_dir = Path(dir_path).parent
        static_dir = project_dir / 'static'
        hyp_name = f"hyp_{name.split(' ')[0].lower()}.json"
        hyp_path = static_dir / hyp_name
        if hyp_path.exists():
            self.hyp = self.HypLoader(hyp_path)
        else:
            self.hyp = {}

        self.test_name = name
        self.test_dir = dir_path
        self.batches = self.find_batches() # batches[1] = 1st Batch results paths
        self.batches_num = len(self.batches)
        self.batch = {}
        for i in range(self.batches_num):
            self.batch[i+1] = MY_BATCH(test_name=self.test_name, 
                                       batch_num = i+1, 
                                       batch_paths = self.batches[i+1], 
                                       no_gap = no_gap, 
                                       hyp = self.hyp)

    def HypLoader(self, hyp_path):

        data = hyploader(hyp_path)
        
        return data


    def find_batches(self):

        # Create a regular expression to match ordinals (1st, 2nd, 3rd, etc.)
        ordinal_regex = re.compile(r"\b(\d+)(st|nd|rd|th)\b")

        # Initialize a dictionary to hold the groups of directories
        batches = {}

        subdirectories = [x for x in self.test_dir.glob("*/") if x.is_dir()]
        for subdirectory in subdirectories:
            # Check if the subdirectory name contains an ordinal
            match = ordinal_regex.search(subdirectory.name)
            if match:
                # Get the ordinal number and convert it to an integer
                ordinal_number = int(match.group(1))
                # Add the subdirectory to the appropriate group
                if ordinal_number not in batches:
                    batches[ordinal_number] = []
                batches[ordinal_number].append(subdirectory)

        # # Print the results
        # for key in sorted(batches.keys()):
        #     print("batches[{}] = {}".format(key, batches[key]))
        
        return batches
    
    
    def info(self):

        output_text = f"In {self.test_name} Test, we have: \n"
        for num, batch in self.batches.items():
            output_text += f"Batch {num} : {batch} \n"
        
        print(output_text)
