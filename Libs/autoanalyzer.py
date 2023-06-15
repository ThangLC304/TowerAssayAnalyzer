from pathlib import Path
from Libs.batchprocess import MY_DIR
from Libs.misc import append_df_to_excel, get_sheet_names, merge_cells, excel_polish, find_existed_batches
import pandas as pd
import json
import time
from tqdm import tqdm
import os
import logging

# Get a logger
logger = logging.getLogger(__name__)

tests = ['Novel Tank', 
         'Shoaling', 
         'Mirror Biting', 
         'Social Interaction', 
         'Predator Avoidance']

TESTLIST = ['Novel Tank Test', 
                'Shoaling Test', 
                'Mirror Biting Test',
                'Social Interaction Test',
                'Predator Test']

hyp_names = ['hyp_novel.json',
            'hyp_shoaling.json',
            'hyp_mirror.json',
            'hyp_social.json',
            'hyp_predator.json']

ORDINALS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']

keywords = [x.split(' ')[0].lower() for x in tests]
EXCEL_NAMES = [f"0{i+1} - {tests[i]} Test (Summary).xlsx" for i in range(len(tests))]

def find_treatments(mother_dir, batch_num):

    control_dirs = [path for path in mother_dir.glob("**/*Control*") if path.is_dir()]

    if control_dirs:
        _ = control_dirs[0]
    else:
        raise Exception("No control directory found.")

    control_dir = Path(control_dirs[0])
    parent_dir = control_dir.parent
    batch_ord = f"{ORDINALS[int(batch_num)-1]} Batch"
    same_level_dirs = [path for path in parent_dir.iterdir() if path.is_dir() and batch_ord in path.name]
    logger.debug(f"Same level dirs with batch ord {batch_ord}: {same_level_dirs}")
    substance_dict = {}
    parameters_required_dict = {}
    for dir_path in same_level_dirs:
        key = dir_path.name.split('-')[0].strip()

        substance = dir_path.name.split('-')[1].split('(')[0].strip()
        substance_dict[key] = substance

        fish_count = len([x for x in dir_path.iterdir() if x.is_dir()])
        logger.debug(f"Found {fish_count} fish in {dir_path.name}")
        parameters_required = 0
        if fish_count == 0:
            parameters_required = 0
        else:
            valid = 0
            #for all subfolders in dir_path, check how many of them has a .txt file inside
            for subfolder in dir_path.iterdir():
                txt_files = [x for x in subfolder.iterdir() if x.is_file() and x.suffix == '.txt']
                if txt_files != []:
                    logger.debug(f"Found {len(txt_files)} txt files in {subfolder.name}")
                    valid += 1
                    logger.debug(f"Valid is now {valid}")
            if valid == 0:
                parameters_required = 0
            else:
                parameters_required = fish_count

        parameters_required_dict[key] = parameters_required

    return substance_dict, parameters_required_dict

def get_current_params_count(project_dir='a path', batch_num=1, task='a task', treatment_index='A'):
    static_path = project_dir / 'static'
    static_batch_path = static_path / f'Batch {batch_num}'
    static_treatment_path = static_batch_path / treatment_index
    task_index = TESTLIST.index(task)
    hyp_name = hyp_names[task_index]
    hyp_path = static_treatment_path / hyp_name

    logger.debug("Loading hyp file from {}".format(hyp_path))
    with open(hyp_path, 'r') as f:
        hyp = json.load(f)

    params_count = 0
    for k, v in hyp.items():
        if isinstance(v, dict):
            params_count = len(v.keys())
            logger.debug(f"Found {params_count} parameters in {k}")

    return params_count

def autoanalyzer(PROJECT_DIR, BATCHNUM, TASK, PROGRESS_BAR, OVERWRITE = False, skip_list = {}):

    TREATMENTS, PARAMS_REQUIRED = find_treatments(PROJECT_DIR, BATCHNUM)

    # PROJECT_DIR, BATCHNUM, TASK, TREATMENTS
    for treatment_index in TREATMENTS.keys():
        # Find the number of fish in each condition
        required_params = PARAMS_REQUIRED[treatment_index]
        logger.debug(f"Required params for {treatment_index} is {required_params}")
        current_params = get_current_params_count(project_dir=PROJECT_DIR, batch_num=BATCHNUM, task=TASK, treatment_index=treatment_index)
        logger.debug(f"Current params for {treatment_index} is {current_params}")
        if required_params != current_params:
            notification = f"{treatment_index};{required_params};{current_params}"
            total_time = 0
            ERROR = "Mismatched"
            return total_time, notification, ERROR

    # PARAMETERS_PATH = PROJECT_DIR / 'static'

    # Get all immediate subdirectories of PROJECT_DIR
    subdirectories = [x for x in PROJECT_DIR.glob("*/") if x.is_dir()]
    TESTS = {}
    for subdirectory in subdirectories:
        if keywords[0] in subdirectory.name.lower():
            TESTS[0] = MY_DIR(name=tests[0], dir_path=subdirectory)
        elif keywords[1] in subdirectory.name.lower():
            TESTS[1] = MY_DIR(name=tests[1], dir_path=subdirectory, no_gap = True)
        elif keywords[2] in subdirectory.name.lower():
            TESTS[2] = MY_DIR(name=tests[2], dir_path=subdirectory)
        elif keywords[3] in subdirectory.name.lower():
            TESTS[3] = MY_DIR(name=tests[3], dir_path=subdirectory)
        elif keywords[4] in subdirectory.name.lower():
            TESTS[4] = MY_DIR(name=tests[4], dir_path=subdirectory)

    # CHECK POINT 1
    logger.info(f'Loaded {len(TESTS)} tests: {[TESTLIST[int(t)] for t in list(TESTS.keys())]}')

    def extract_data(test_num, batch_num, cond):
        fishes = {}
        fish_ids = [k for k in TESTS[test_num].batch[batch_num].condition[cond].targets.keys()]    
        PARAMETERS_PATH = TESTS[test_num].batch[batch_num].condition[cond].hyp_path
        # logger.info(f"Skip list: {skip_list[cond]}")
        # merge fish_ids and skip_list, then remove duplicates
        # fish_ids = list(set(fish_ids + skip_list[cond]))
        # sort in numerical value order: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
        fish_ids = sorted(fish_ids, key=lambda x: int(x))
        logger.info(f"Fish IDs: {fish_ids}")
        SEGMENTED_DATA = False    
        if test_num == 0:
            # json_name = f"hyp_{keywords[test_num]}.json"
            # json_path = PARAMETERS_PATH / json_name
            json_path = PARAMETERS_PATH
            with open(json_path, 'r') as f:
                hyp = json.load(f)
            try:
                temp_duration = int(float(hyp["DURATION"]))
                temp_segment_duration = int(float(hyp["SEGMENT DURATION"]))
                seg_num = int(temp_duration/temp_segment_duration)
                SEGMENTED_DATA = True
            except:
                SEGMENTED_DATA = False

        if SEGMENTED_DATA == True:
            for fish_id in tqdm(fish_ids, desc="Analyzing Fish"):       
                tqdm.write(f'Fish {fish_id}...')
                fishes[fish_id] = TESTS[test_num].batch[batch_num].condition[cond].analyze(str(fish_id), seg_num)
                # fishes[fish_id] = *executor.*exec.result_dict[f"{segment*wait}-{segment*wait+1} MIN"] = test.rows

        if SEGMENTED_DATA == False:
            for fish_id in tqdm(fish_ids, desc="Analyzing Fish"):       
                tqdm.write(f'Fish {fish_id}...')
                fishes[fish_id] = TESTS[test_num].batch[batch_num].condition[cond].analyze(str(fish_id))

        return fishes



    class NovelBatch():

        def __init__(self, batch_num, cond, wait = 5):

            # NovelBatch means test_num = 0
            self.test_num = 0
            self.wait = wait
            
            self.batch_num = batch_num
            self.condition = cond

            self.excel_name = EXCEL_NAMES[self.test_num]
            self.excel_path = PROJECT_DIR / self.excel_name

        
        def analyze(self):

            # Extract data according to input
            logger.info(f"Extracting data {self.batch_num} - {self.condition}...")
            self.test_result = extract_data(self.test_num, self.batch_num, self.condition)
            logger.info(f"Extracted {len(self.test_result)} fishes data")
            logger.info(f"Fish list: {list(self.test_result.keys())}")

            if self.test_result == {}:
                logger.warning(f"No data found for test {self.test_num} batch {self.batch_num} condition {self.condition}.")
                return

            self.dfs = {}

            example_key = list(self.test_result.keys())[0]

            for segment in self.test_result[example_key].keys():
                self.dfs[segment] = pd.DataFrame()

            logger.info("Rearrange into dataframe...")
            for segment in self.test_result[example_key].keys():
                for fish in self.test_result.keys():
                    logger.debug(f"Organizing data of fish {fish}...")
                    df = self.get_case_df(fish, segment)
                    # if self.df is empty, then just assign df to self.df
                    if self.dfs[segment].empty:
                        self.dfs[segment] = df
                    else:
                        self.dfs[segment] = pd.concat([self.dfs[segment], df], ignore_index=True)
                
                self.dfs[segment] = self.dfs[segment].reset_index(drop=True)

                # add index column = fish ids
                index_col = [f'Fish {i+1}' for i in range(len(self.dfs[segment]))]
                self.dfs[segment]['Fish ID'] = index_col
                self.dfs[segment].set_index('Fish ID', inplace=True)


            logger.info("Exporting to excel...")
            self.export_to_excel()


        def get_case_df(self, key, subkey): # key = fish id, subkey = timestamp
            
            logger.debug(f"Dealing with key: {key}, key type = {type(key)}")
            logger.debug(f"and subkey: {subkey}, subkey type = {type(subkey)}")
            # Normalize the input
            key = str(key)
            
            case_dict = self.test_result[key][subkey]

            # Create df based on extracted data
            try:
                columns = [x[0] for x in case_dict.values()]
            except:
                logger.debug(f"Case dict: {case_dict}")
            units = [x[2] for x in case_dict.values()]
            for i in range(len(columns)):
                if units[i] != '':
                    columns[i] = columns[i] + ' (' + units[i] + ')'
                
            df = pd.DataFrame(columns=columns)
            first_row = [x[1] for x in case_dict.values()]
            df.loc[0] = first_row

            return df
        

        def export_to_excel(self):
            
            if self.excel_path.exists():
                header = False
                logger.debug("Excel file exists, appending to existing file...")
            else:
                header = True
                logger.debug("Excel file does not exist, creating new file...")

            logger.info("Exporting to excel...")
            logger.debug(f"Keys in dfs: {self.dfs.keys()}")
            logger.debug(f"Excel path: {self.excel_path}")

            for segment in self.dfs.keys():
                logger.debug(f"Exporting sheet {segment}...")
                try:
                    append_df_to_excel(self.excel_path, self.dfs[segment], sheet_name=segment, startcol = 2, index=True, header=header)
                except:
                    logger.error(f"Export sheet {segment} failed.")
                    continue
                # open the excel file to adjust the column width
                # use openpyxl to open excel_path, go to each sheet to change columns width to fit content
                logger.info("Sheet name " + segment + " exported to excel successfully.")

            logger.info(f"All sheets exported to {self.excel_name} successfully.")
            logger.info("Polishing excel file...")
            try:
                excel_polish(self.excel_path, 
                         batch_num=self.batch_num, 
                         cell_step=10, 
                         treatment = TREATMENTS[self.condition],
                         inplace=True)
            except Exception as e:
                logger.error("Excel polishing failed.")
                logger.error(e)
                raise e

        def __repr__(self):
            return self.dfs.__repr__()
        


    class ShoalingBatch():

        def __init__(self, batch_num, cond):

            # ShoalingBatch means test_num = 1
            self.test_num = 1

            self.condition = cond

            self.batch_num = batch_num

            self.excel_name = EXCEL_NAMES[self.test_num]

            self.excel_path = PROJECT_DIR / self.excel_name
            

        def analyze(self):
            
            # Extract data according to input
            print(f"Extracting data {self.batch_num} - {self.condition}...")
            self.test_result = extract_data(self.test_num, self.batch_num, self.condition)

            if self.test_result == {}:
                logger.warning(f"No data found for test {self.test_num} batch {self.batch_num} condition {self.condition}.")
                return

            self.dfs = {}

            print("Rearrange into dataframe...")
            for fishgroup in self.test_result.keys():
                self.dfs[fishgroup] = pd.DataFrame()
                for fish in self.test_result[fishgroup].keys():
                    if fish == 'Common':
                        continue
                    df = self.get_case_df(fishgroup, fish)
                    # if self.df is empty, then just assign df to self.df
                    if self.dfs[fishgroup].empty:
                        self.dfs[fishgroup] = df
                    else:
                        self.dfs[fishgroup] = pd.concat([self.dfs[fishgroup], df], ignore_index=True)

                self.dfs[fishgroup] = self.dfs[fishgroup].reset_index(drop=True)
                # Add column of Average inter-fish distance
                avg_inter_distance = [v[1] for k, v in self.test_result[fishgroup]['Common'].items() if k != 0]
                self.dfs[fishgroup]['Average inter-fish distance (cm)'] = avg_inter_distance
                # Add column of Shoaling Area
                shoaling_area = self.test_result[fishgroup]['Common'][0][1]
                self.dfs[fishgroup]['Shoaling Area (cm^2)'] = [shoaling_area, 0, 0]

                # add index column = fish ids
                fishgroup_index = list(self.test_result.keys()).index(fishgroup)
                index_col = [f'Fish {i+1+fishgroup_index*3}' for i in range(len(self.dfs[fishgroup]))]
                self.dfs[fishgroup]['Fish ID'] = index_col
                self.dfs[fishgroup].set_index('Fish ID', inplace=True)

            print("Exporting to excel...")
            self.export_to_excel()


        def get_case_df(self, key, subkey): # key = fish id, subkey = timestamp
            
            # Normalize the input
            key = str(key)

            case_dict = self.test_result[key][subkey]

            # Create df based on extracted data
            columns = [x[0] for x in case_dict.values()]
            units = [x[2] for x in case_dict.values()]
            for i in range(len(columns)):
                if units[i] != '':
                    columns[i] = columns[i] + ' (' + units[i] + ')'
                
            df = pd.DataFrame(columns=columns)
            first_row = [x[1] for x in case_dict.values()]
            df.loc[0] = first_row

            return df
        

        def export_to_excel(self):
            
            header = True
            if self.excel_path.exists():
                # check if the sheet already exists
                # if yes, then header = False
                # if no, then header = True

                if TREATMENTS[self.condition] in get_sheet_names(self.excel_path):
                    header = False
                    logger.debug("Header = False, appending to existing sheet...")
                else:
                    header = True
                    logger.debug("Header = True, creating new sheet...")

            logger.info("Exporting to excel...")
            logger.debug(f"Keys in dfs: {self.test_result.keys()}")
            logger.debug(f"Excel path: {self.excel_path}")
                
            for i, fishgroup in enumerate(self.test_result.keys()):
                if i > 0:
                    header = False
                    logger.debug("Header = False, appending to existing sheet...")
                try:
                    append_df_to_excel(self.excel_path, self.dfs[fishgroup], sheet_name=TREATMENTS[self.condition], startcol = 2, index=True, header = header)
                except:
                    logger.error(f"Export {fishgroup} failed.")
                    continue
                # open the excel file to adjust the column width
                # use openpyxl to open excel_path, go to each sheet to change columns width to fit content
            print("Sheet name " + TREATMENTS[self.condition] + " exported to excel successfully.")

            merge_cells(self.excel_path, col_name='Shoaling Area', cell_step=3, inplace=True)
            excel_polish(self.excel_path, batch_num=self.batch_num, cell_step=9, inplace=True)



        def __repr__(self):
            return self.dfs.__repr__()
    


    class NormalBatch():

        def __init__(self, test_num, batch_num, cond):

            # Other Tests use a common NormalBatch class, hence the test_num is needed
            self.test_num = test_num

            self.condition = cond
            
            self.batch_num = batch_num

            self.excel_name = EXCEL_NAMES[self.test_num]

            self.excel_path = PROJECT_DIR / self.excel_name


        def analyze(self):
             # Extract data according to input
            print(f"Extracting data {self.batch_num} - {self.condition}...")
            self.test_result = extract_data(self.test_num, self.batch_num, self.condition)

            if self.test_result == {}:
                logger.warning(f"No data found for test {self.test_num} batch {self.batch_num} condition {self.condition}.")
                return

            self.df = pd.DataFrame()

            for fish in self.test_result.keys():
                df = self.get_case_df(fish)
                if self.df.empty:
                    self.df = df
                else:
                    self.df = pd.concat([self.df, df], ignore_index=True)

            # add index column = fish ids
            self.df['Fish ID'] = [f'Fish {i}' for i in list(self.test_result.keys())]
            self.df.set_index('Fish ID', inplace=True)

            print("Exporting to excel...")
            self.export_to_excel()


        def get_case_df(self, key): # key = fish id, subkey = timestamp

            case_dict = self.test_result[key]

            # Create df based on extracted data
            columns = [x[0] for x in case_dict.values()]
            units = [x[2] for x in case_dict.values()]
            for i in range(len(columns)):
                if units[i] != '':
                    columns[i] = columns[i] + ' (' + units[i] + ')'
                
            df = pd.DataFrame(columns=columns)
            first_row = [x[1] for x in case_dict.values()]
            df.loc[0] = first_row

            return df
        

        def export_to_excel(self):
            
            header = True
            if self.excel_path.exists():
                # check if the sheet already exists
                # if yes, then header = False
                # if no, then header = True

                if TREATMENTS[self.condition] in get_sheet_names(self.excel_path):
                    header = False
                    logger.debug("Excel file exists, appending to existing file...")
                else:
                    header = True
                    logger.debug("Excel file does not exist, creating new file...")

            logger.info("Exporting to excel...")
            logger.debug(f"Keys in df: {self.df.keys()}")
            logger.debug(f"Excel path: {self.excel_path}")


            append_df_to_excel(self.excel_path, self.df, sheet_name=TREATMENTS[self.condition], startcol = 1, index=True, header = header)
            # open the excel file to adjust the column width
            # use openpyxl to open excel_path, go to each sheet to change columns width to fit content
            print("Sheet name " + TREATMENTS[self.condition] + " exported to excel successfully.")

            logger.info("Polishing excel file...")
            try:
                excel_polish(self.excel_path, 
                            batch_num=self.batch_num, 
                            cell_step=10, 
                            inplace=True)
            except Exception as e:
                logger.error("Excel polishing failed.")
                logger.error(e)
                raise e


        def __repr__(self):
            return self.dfs.__repr__()
        

    def first_check(test_num):

        excel_name = EXCEL_NAMES[test_num]
        excel_path = PROJECT_DIR / excel_name

        # if test_num == 0:
        #     repetition = 3
        # else:
        #     repetition = 1

        if excel_path.exists():
            existed_batch = find_existed_batches(excel_path)
        else:
            existed_batch = {}

        if excel_path.exists():
            try:
                #rename to same name to check if the file is opened
                os.rename(excel_path, excel_path)
            except OSError:
                total_time = time.time() - time00
                notification = f'Please close the excel file {excel_name} before running the program.'
                ERROR = "File Opened"
                return total_time, notification, ERROR

        if f"Batch {BATCHNUM}" in existed_batch.keys():
            if OVERWRITE == False:
                ERROR = "Existed"
                notification = f'Batch {BATCHNUM} has already been analyzed.'
                total_time = time.time() - time00
                return total_time, notification, ERROR
            else:
                #[TODO] THE OVERWRITE FUNCTION SHOULD ONLY DELETE THE OLD VERSION OF SELECTED BATCH
                # NOT THE WHOLE EXCEL FILE!
                try:
                    logger.info("Overwriting the existing excel file...")
                    os.remove(excel_path)
                except OSError:
                    total_time = time.time() - time00
                    notification = f'Please close the excel file {excel_name} before running the program.'
                    ERROR = "File Opened"
                    return total_time, notification, ERROR
                
                return None, None, None
            
        return None, None, None    

    

    ERROR = None

    print()
    print('='*50)
    print(f"START ANALYZING BATCH {BATCHNUM} ...")
    print('='*50)
    print()
    time00 = time.time()

    # =========================================================
    


    if TASK == TESTLIST[0]:

        print('Analyzing Novel Tank Test...')

        test_num = 0

        if first_check(test_num) != (None, None, None):
            total_time, notification, ERROR = first_check(test_num)
            return total_time, notification, ERROR
        
        time0 = time.time()

        i = 0
        for cond in TREATMENTS.keys():
            current_batch = NovelBatch(batch_num=BATCHNUM, cond=cond) 
            current_batch.analyze()

            progress = (i + 1) / len(TREATMENTS) * 100
            PROGRESS_BAR['value'] = progress
            PROGRESS_BAR.update()
            i += 1

            print()


        time1 = time.time()
        print(f'... time taken: {time1 - time0} seconds')
        print('='*50)
        print()

    # =========================================================

    elif TASK == TESTLIST[1]:

        print('Analyzing Shoaling Test...')

        test_num = 1
        # row_per_batch = 9

        if first_check(test_num) != (None, None, None):
            total_time, notification, ERROR = first_check(test_num)
            return total_time, notification, ERROR

        time0 = time.time()

        i = 0
        for cond in TREATMENTS.keys():
            current_batch = ShoalingBatch(batch_num=BATCHNUM, cond=cond)
            current_batch.analyze()

            progress = (i + 1) / len(TREATMENTS) * 100
            PROGRESS_BAR['value'] = progress
            PROGRESS_BAR.update()
            i += 1

            print()

        time1 = time.time()

        print(f'... time taken: {time1 - time0} seconds')
        print('='*50)
        print()

    # =========================================================

    else:
        test_num = TESTLIST.index(TASK)

        print(f'Analyzing {tests[test_num]} Test...')

        # row_per_batch = 10

        if first_check(test_num) != (None, None, None):
            total_time, notification, ERROR = first_check(test_num)
            return total_time, notification, ERROR

        time0 = time.time()

        i = 0
        for cond in TREATMENTS.keys():
            current_batch = NormalBatch(test_num=test_num, batch_num=BATCHNUM, cond=cond)
            current_batch.analyze()

            progress = (i + 1) / len(TREATMENTS) * 100
            PROGRESS_BAR['value'] = progress
            PROGRESS_BAR.update()
            i += 1

            print()

        time1 = time.time()

        print(f'... time taken: {time1 - time0} seconds') 
        print('='*50)
        print()

    # =========================================================

    notification = f'Batch {BATCHNUM} has been analyzed successfully.'
    print(notification)
    time11 = time.time()
    total_time = time11 - time00
    print()
    print(f'Total time taken: {total_time} seconds')
    print()
    print('='*50)
    print()

    return total_time, notification, ERROR

