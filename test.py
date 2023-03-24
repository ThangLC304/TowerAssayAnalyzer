from Libs.executor import *

def noveltest():
    txt_path = "Input/Zebrafish Tower/A - Novel Tank Test/trajectories.txt"
    display_dict = noveltank_exec(txt_path)
    for content in display_dict.values():
        print(content[0], content[1], content[2])

def shoalingtest():
    txt_path = "Input/Zebrafish Tower/B - Shoaling Test/trajectories_nogaps.txt"
    display_dict = shoaling_exec(txt_path)
    for content in display_dict.values():
        print(content[0], content[1], content[2])

if __name__ == "__main__":
    shoalingtest()