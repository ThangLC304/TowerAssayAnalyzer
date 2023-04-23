from pathlib import Path
from Libs.batchprocess import MY_DIR
from Libs.misc import append_df_to_excel, adjust_column_widths, get_sheet_names, merge_cells
import pandas as pd
import json
import time
from tqdm import tqdm


tests = ['Novel Tank', 'Shoaling', 'Mirror Biting', 'Social Interaction', 'Predator Avoidance']
keywords = [x.split(' ')[0].lower() for x in tests]
EXCEL_NAMES = [f"0{i+1} - {tests[i]} Test (Summary).xlsx" for i in range(len(tests))]

def find_treatments(mother_dir):

    control_dirs = [path for path in mother_dir.glob("**/*Control*") if path.is_dir()]

    if control_dirs:
        control_dir_path = control_dirs[0]
    else:
        print("No Control directory found.")

    control_dir = Path(control_dirs[0])
    parent_dir = control_dir.parent
    same_level_dirs = [path for path in parent_dir.iterdir() if path.is_dir()]

    result_dict = {}
    for dir_path in same_level_dirs:
        key = dir_path.name.split('-')[0].strip()
        substance = dir_path.name.split('-')[1].split('(')[0].strip()
        result_dict[key] = substance

    return result_dict

def autoanalyzer(PROJECT_DIR, BATCHNUM, TASK, PROGRESS_BAR):

    TREATMENTS = find_treatments(PROJECT_DIR)

    PARAMETERS_PATH = PROJECT_DIR / 'static'

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
    if len(TESTS) == 5:
        print('TESTS data structure loaded successfully.')

    def extract_data(test_num, batch_num, cond):
        fishes = {}
        fish_ids = [k for k in TESTS[test_num].batch[batch_num].condition[cond].targets.keys()]    
        print(fish_ids)
        SEGMENTED_DATA = False    
        if test_num == 0:
            json_name = f"hyp_{keywords[test_num]}.json"
            json_path = PARAMETERS_PATH / json_name
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
            
            # Extract data according to input
            print("Extracting data...")
            self.test_result = extract_data(self.test_num, batch_num, cond)

            # print("Test result:", self.test_result)

            self.dfs = {}

            example_key = list(self.test_result.keys())[0]

            for segment in self.test_result[example_key].keys():
                self.dfs[segment] = pd.DataFrame()

            print("Rearrange into dataframe...")
            for segment in self.test_result[example_key].keys():
                for fish in self.test_result.keys():
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
            excel_name = EXCEL_NAMES[self.test_num]
            excel_path = PROJECT_DIR / excel_name
            if excel_path.exists():
                header = False
            else:
                header = True
            for segment in self.dfs.keys():
                append_df_to_excel(excel_path, self.dfs[segment], sheet_name=segment, startcol = 2, index=True, header=header)
                # open the excel file to adjust the column width
                # use openpyxl to open excel_path, go to each sheet to change columns width to fit content
                print("Sheet name " + segment + " exported to excel successfully.")

            adjust_column_widths(excel_path)
            print(f"All sheets exported to {excel_name} successfully.")


        def __repr__(self):
            return self.dfs.__repr__()
        


    class ShoalingBatch():

        def __init__(self, batch_num, cond):

            # ShoalingBatch means test_num = 1
            self.test_num = 1

            self.condition = cond
            
            # Extract data according to input
            print("Extracting data...")
            self.test_result = extract_data(self.test_num, batch_num, cond)

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
            excel_name = EXCEL_NAMES[self.test_num]
            excel_path = PROJECT_DIR / excel_name
            header = True
            if excel_path.exists():
                # check if the sheet already exists
                # if yes, then header = False
                # if no, then header = True

                if TREATMENTS[self.condition] in get_sheet_names(excel_path):
                    header = False
                else:
                    header = True
                
            for i, fishgroup in enumerate(self.test_result.keys()):
                if i > 0:
                    header = False
                append_df_to_excel(excel_path, self.dfs[fishgroup], sheet_name=TREATMENTS[self.condition], startcol = 2, index=True, header = header)
                # open the excel file to adjust the column width
                # use openpyxl to open excel_path, go to each sheet to change columns width to fit content
            print("Sheet name " + TREATMENTS[self.condition] + " exported to excel successfully.")

            adjust_column_widths(excel_path)
            merge_cells(excel_path, col_name='Shoaling Area', cell_step=3, inplace=True)


        def __repr__(self):
            return self.dfs.__repr__()
    


    class NormalBatch():

        def __init__(self, test_num, batch_num, cond):

            # Other Tests use a common NormalBatch class, hence the test_num is needed
            self.test_num = test_num

            self.condition = cond
            
            # Extract data according to input
            print("Extracting data...")
            self.test_result = extract_data(self.test_num, batch_num, cond)

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

            excel_name = EXCEL_NAMES[self.test_num]
            excel_path = PROJECT_DIR / excel_name
            header = True
            if excel_path.exists():
                # check if the sheet already exists
                # if yes, then header = False
                # if no, then header = True

                if TREATMENTS[self.condition] in get_sheet_names(excel_path):
                    header = False
                else:
                    header = True
                
            append_df_to_excel(excel_path, self.df, sheet_name=TREATMENTS[self.condition], startcol = 1, index=True, header = header)
            # open the excel file to adjust the column width
            # use openpyxl to open excel_path, go to each sheet to change columns width to fit content
            print("Sheet name " + TREATMENTS[self.condition] + " exported to excel successfully.")

            adjust_column_widths(excel_path)


        def __repr__(self):
            return self.dfs.__repr__()
        
    print()
    print('='*50)
    print(f"START ANALYZING {BATCHNUM} ...")
    print('='*50)
    print()
    time00 = time.time()

    # =========================================================
    TESTLIST = ['Novel Tank Test', 
                'Shoaling Test', 
                'Mirror Biting Test',
                'Social Interaction Test',
                'Predator Test']


    if TASK == TESTLIST[0]:

        print('Analyzing Novel Tank Test...')
        time0 = time.time()

        i = 0
        for cond in TREATMENTS.keys():
            _ = NovelBatch(batch_num=BATCHNUM, cond=cond) 

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
        time0 = time.time()

        time0 = time.time()

        i = 0
        for cond in TREATMENTS.keys():
            _ = ShoalingBatch(batch_num=BATCHNUM, cond=cond)

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
        num = TESTLIST.index(TASK)

    # for num in range(2, 5):
        print(f'Analyzing {tests[num]} Test...')
        time0 = time.time()

        i = 0
        for cond in TREATMENTS.keys():
            _ = NormalBatch(test_num=num, batch_num=BATCHNUM, cond=cond)

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

    print('Batch Analysis COMPLETED !')
    time11 = time.time()
    total_time = time11 - time00
    print()
    print(f'Total time taken: {total_time} seconds')
    print()
    print('='*50)
    print()

    return total_time

