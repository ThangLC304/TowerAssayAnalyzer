from Libs.analyzer import *
from Libs.general import upper_first
from Libs.misc import load_raw_df, clean_df


basic_requirements = ['total distance', 'average speed', 
                      'freezing percentage', 'swimming percentage', 'rapid movement percentage'] 
                    

class NovelTank_Display(NovelTankTest):

    def __init__(self, input_df, segment = -1):

        super().__init__(input_df, segment)

        self.rows = {}
        for i, req in enumerate(basic_requirements):
            self.rows[i] = [upper_first(req), self.basic[req], self.units[req]]

        try:
            average_entry = self.time.duration/self.events.count
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
            ['Number of entries', self.events.count, ''],
            ['Average entry', average_entry, 'seconds']
        ]

        for j in range(i, len(self.display)+i):
            self.rows[j] = self.display[j-i]


    

def noveltank_exec(txt_path, seg_num = 1, wait = 5):

    # wait time between each record session is 5 minutes

    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    result_dict = {}
    

    result_dict['whole'] = NovelTank_Display(df, segment = -1).rows

    if seg_num > 1:
        for segment in range(seg_num):
            test = NovelTank_Display(df, segment = segment)
            result_dict[f"{segment*wait}-{segment*wait+1} MIN"] = test.rows

    return result_dict
        



class Shoaling_Display(ShoalingTest):

    def __init__(self, input_df1, input_df2, input_df3):

        super().__init__(input_df1, input_df2, input_df3)

        self.basicdisplay = {}

        for df_num in range(1, 4):
            self.basicdisplay[df_num] = {}
            for i, req in enumerate(basic_requirements):
                self.basicdisplay[df_num][i] = [upper_first(req), self.basic[df_num][req], self.units[req]]

            temp_time, _ = self.timing(self.df[df_num], "TOP", "X", smaller = True)
            self.basicdisplay[df_num][i+1] = ['Time in top', temp_time.percentage, temp_time.unit]

            distance_to_center = self.distance_to(self.df[df_num], "CENTER")
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


def shoaling_exec(txt_path):

    whole_df, _ = load_raw_df(txt_path)
    whole_df, _ = clean_df(whole_df, fill=True)
    df1, df2, df3 = whole_df.iloc[:, :2], whole_df.iloc[:, 2:4], whole_df.iloc[:, 4:]
    # print('Splitted into 3 dataframes', df1.shape, df2.shape, df3.shape, '')
    test = Shoaling_Display(df1, df2, df3)
    result_dict = {}
    result_dict['Fish A'] = test.basicdisplay[1]
    result_dict['Fish B'] = test.basicdisplay[2]
    result_dict['Fish C'] = test.basicdisplay[3]
    result_dict['Common'] = test.commondisplay
    return result_dict



class MirrorBiting_Display(MirrorBitingTest):

    def __init__(self, input_df):

        super().__init__(input_df)

        self.rows = {}
        for i, req in enumerate(basic_requirements):
            self.rows[i] = [upper_first(req), self.basic[req], self.units[req]]

        self.display = [
            ['Mirror biting time', self.time.percentage, '%'],
            ['Longest time mirror biting', self.events.longest, self.events.unit],
            ['Longest time mirror biting %', self.events.percentage, '%'],
        ]

        for j in range(i, len(self.display)+i):
            self.rows[j] = self.display[j-i]


def mirrorbiting_exec(txt_path):
    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    test = MirrorBiting_Display(df)
    return test.rows



class SocialInteraction_Display(SocialInteractionTest):

    def __init__(self, input_df):

        super().__init__(input_df)

        self.rows = {}
        for i, req in enumerate(basic_requirements):
            self.rows[i] = [upper_first(req), self.basic[req], self.units[req]]

        self.display = [
            ['Interaction time', self.time.percentage, '%'],
            ['Longest time in interaction', self.events.longest, self.events.unit],
            ['Longest time in interaction %', self.events.percentage, '%'],
            ['Average distance to separator', self.distance.avg, self.distance.unit],
        ]

        for j in range(i, len(self.display)+i):
            self.rows[j] = self.display[j-i]


def socialinteraction_exec(txt_path):
    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    test = SocialInteraction_Display(df)
    return test.rows



class PredatorAvoidance_Display(PredatorAvoidanceTest):

    def __init__(self, input_df):

        super().__init__(input_df)

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

        for j in range(i, len(self.display)+i):
            self.rows[j] = self.display[j-i]


def predatoravoidance_exec(txt_path):
    df, _ = load_raw_df(txt_path)
    df, _ = clean_df(df, fill=True)
    test = PredatorAvoidance_Display(df)
    return test.rows