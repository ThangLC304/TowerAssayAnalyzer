from Libs.analyzer import *
from Libs.general import upper_first
from Libs.misc import load_raw_df, clean_df


basic_requirements = ['total distance', 'average speed', 
                      'freezing percentage', 'swimming percentage', 'rapid movement percentage'] 

def get_fish_num(txt_path):

    fish_num = Path(txt_path).parent.name
    # if " " or "-" or "_" in fish_num:
    # take only the number before the first space, dash or underscore
    if " " in fish_num:
        fish_num = fish_num.split(' ')[0].strip()
    elif "-" in fish_num:
        fish_num = fish_num.split('-')[0].strip()
    elif "_" in fish_num:
        fish_num = fish_num.split('_')[0].strip()
    
    return fish_num


class NovelTank_Display(NovelTankTest):

    def __init__(self, input_df, project_hyp, fish_num, segment = -1):

        super().__init__(input_df, project_hyp, fish_num, segment)

        self.rows = {}
        for i, req in enumerate(basic_requirements):
            self.rows[i] = [upper_first(req), self.basic[req], self.units[req]]

        try:
            average_entry = self.time.duration/self.events.count/self.hyp["FPS"]
        except:
            average_entry = 0

        self.display = [
            ['Average distance to center', self.distance.avg, self.distance.unit],
            ['Time in top', self.time.percentage, '%'],
            ['Time in bottom', self.time.not_percentage, '%'],
            ['Time spent in top/bottom ratio', self.others['top/bottom ratio'], ''],
            ['Distance traveled in top', self.others['distance in top'], self.distance.unit],
            ['Distance traveled top/bottom ratio', self.others['distance top/bottom ratio'], ''],
            ['Latency in frames', self.others['latency in frames'], 'frames'],
            ['Latency in seconds', self.others['latency in seconds'], 'seconds'],
            ['Number of entries', self.others['entry number'], ''],
            ['Average entry', self.others['average entry'], 'seconds']
        ]

        # add self.display to self.rows
        for i, row in enumerate(self.display):
            self.rows[i+len(basic_requirements)] = row

    

def noveltank_exec(txt_path, project_hyp, seg_num = 1, wait = 5):

    # wait time between each record session is 5 minutes

    # FISH_NUM IS NEWLY ADDED TO THE FUNCTION TO BE USED AS KEY FOR HYPERPARAMETER DICT
    fish_num = get_fish_num(txt_path)

    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    result_dict = {}
    

    result_dict['whole'] = NovelTank_Display(df, project_hyp = project_hyp, fish_num=fish_num, segment = -1).rows

    if seg_num > 1:
        for segment in range(seg_num):
            test = NovelTank_Display(df, project_hyp = project_hyp, fish_num=fish_num, segment = segment)
            result_dict[f"{segment*wait}-{segment*wait+1} MIN"] = test.rows

    return result_dict
        



class Shoaling_Display(ShoalingTest):

    def __init__(self, input_df1, input_df2, input_df3, project_hyp, fish_num):

        super().__init__(input_df1, input_df2, input_df3, project_hyp, fish_num)

        self.basicdisplay = {}

        for df_num in range(1, 4):
            self.basicdisplay[df_num] = {}
            for i, req in enumerate(basic_requirements):
                self.basicdisplay[df_num][i] = [upper_first(req), self.basic[df_num][req], self.units[req]]

            temp_time, _ = self.timing(self.df[df_num], "TOP", fish_num, "X", smaller = True)
            self.basicdisplay[df_num][i+1] = ['Time in top', temp_time.percentage, temp_time.unit]

            distance_to_center = self.distance_to(self.df[df_num], "CENTER", fish_num)
            self.basicdisplay[df_num][i+2] = ['Average distance to center', distance_to_center.avg, distance_to_center.unit]

            near, far = self.distance_filter(df_num)
            self.basicdisplay[df_num][i+3] = ['Nearest distance', near.avg, near.unit]
            self.basicdisplay[df_num][i+4] = ['Furthest distance', far.avg, far.unit]

        shoal_area = self.shoal_area()
        distance_AB = self.distance_to_other(self.df[1], self.df[2])
        distance_BC = self.distance_to_other(self.df[2], self.df[3])
        distance_CA = self.distance_to_other(self.df[3], self.df[1])

        self.commondisplay = {
            0 : ['Shoal area', shoal_area.avg, shoal_area.unit],
            1 : ['Average distance A vs B', distance_AB.avg, distance_AB.unit],
            2 : ['Average distance B vs C', distance_BC.avg, distance_BC.unit],
            3 : ['Average distance C vs A', distance_CA.avg, distance_CA.unit],
        }


def shoaling_exec(txt_path, project_hyp):

    # FISH_NUM IS NEWLY ADDED TO THE FUNCTION TO BE USED AS KEY FOR HYPERPARAMETER DICT
    fish_num = get_fish_num(txt_path)

    whole_df, _ = load_raw_df(txt_path)
    whole_df, _ = clean_df(whole_df, fill=True)
    df1, df2, df3 = whole_df.iloc[:, :2], whole_df.iloc[:, 2:4], whole_df.iloc[:, 4:]
    # print('Splitted into 3 dataframes', df1.shape, df2.shape, df3.shape, '')
    test = Shoaling_Display(df1, df2, df3, project_hyp, fish_num)
    result_dict = {}
    result_dict['Fish A'] = test.basicdisplay[1]
    result_dict['Fish B'] = test.basicdisplay[2]
    result_dict['Fish C'] = test.basicdisplay[3]
    result_dict['Common'] = test.commondisplay
    return result_dict



class MirrorBiting_Display(MirrorBitingTest):

    def __init__(self, input_df, project_hyp, fish_num):

        super().__init__(input_df, project_hyp, fish_num)

        self.rows = {}
        for i, req in enumerate(basic_requirements):
            self.rows[i] = [upper_first(req), self.basic[req], self.units[req]]

        self.display = [
            ['Mirror biting time', self.time.percentage, '%'],
            ['Longest time mirror biting', self.events.longest, self.events.unit],
            ['Longest time mirror biting %', self.events.percentage, '%'],
        ]

        # add self.display to self.rows
        for i, row in enumerate(self.display):
            self.rows[i+len(basic_requirements)] = row


def mirrorbiting_exec(txt_path, project_hyp):

    # FISH_NUM IS NEWLY ADDED TO THE FUNCTION TO BE USED AS KEY FOR HYPERPARAMETER DICT
    fish_num = get_fish_num(txt_path)

    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    test = MirrorBiting_Display(df, project_hyp, fish_num)
    return test.rows



class SocialInteraction_Display(SocialInteractionTest):

    def __init__(self, input_df, project_hyp, fish_num):

        super().__init__(input_df, project_hyp, fish_num)

        self.rows = {}
        for i, req in enumerate(basic_requirements):
            self.rows[i] = [upper_first(req), self.basic[req], self.units[req]]

        self.display = [
            ['Interaction time', self.time.percentage, '%'],
            ['Longest time in interaction', self.events.longest, self.events.unit],
            ['Longest time in interaction %', self.events.percentage, '%'],
            ['Average distance to separator', self.distance.avg, self.distance.unit],
        ]

        # add self.display to self.rows
        for i, row in enumerate(self.display):
            self.rows[i+len(basic_requirements)] = row


def socialinteraction_exec(txt_path, project_hyp):

    # FISH_NUM IS NEWLY ADDED TO THE FUNCTION TO BE USED AS KEY FOR HYPERPARAMETER DICT
    fish_num = get_fish_num(txt_path)

    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    test = SocialInteraction_Display(df, project_hyp, fish_num)
    return test.rows



class PredatorAvoidance_Display(PredatorAvoidanceTest):

    def __init__(self, input_df, project_hyp, fish_num):

        super().__init__(input_df, project_hyp, fish_num)

        self.rows = {}
        for i, req in enumerate(basic_requirements):
            self.rows[i] = [upper_first(req), self.basic[req], self.units[req]]

        self.display = [
            ['Predator avoiding time', self.time.duration, self.time.unit],
            ['Predator avoiding time %', self.time.percentage, '%'],
            ['Predator approaching time', self.time.not_duration, self.time.unit],
            ['Predator approaching time %', self.time.not_percentage, '%'],
            ['Longest time approaching predator', self.events.longest, self.events.unit],
            ['Average distance to predator', self.distance.avg, self.distance.unit],
        ]

        # add self.display to self.rows
        for i, row in enumerate(self.display):
            self.rows[i+len(basic_requirements)] = row


def predatoravoidance_exec(txt_path, project_hyp):

    # FISH_NUM IS NEWLY ADDED TO THE FUNCTION TO BE USED AS KEY FOR HYPERPARAMETER DICT
    fish_num = get_fish_num(txt_path)

    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    test = PredatorAvoidance_Display(df, project_hyp, fish_num)
    return test.rows