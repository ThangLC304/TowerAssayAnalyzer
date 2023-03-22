from misc import *
import time
import cv2
import argparse

im_path = r'C:\Code\ChungyuanProjects\TowerAssayAnalyzer\Input\C - Mirror Biting Test.png'
txt_path = r'C:\Code\ChungyuanProjects\TowerAssayAnalyzer\Output\arranged_C - Mirror Biting Test - full.csv'
# txt_path = r'C:\Code\ChungyuanProjects\TowerAssayAnalyzer\Output\raw_df_withgap.csv'

# Load the image
def main(mode = 'single', time_wait = 10, time_start = 0, frame_step = 50, tracked_tank = 0):
    final_df_1, im_1, tanks_list_1 = draw_prep(mode = mode, im_path = im_path, txt_path = txt_path)

    limit = len(final_df_1)

    time = time_start
    while True:
        print('Time frame: ', time)
        draw_trajectories(final_df_1, im_1, tanks_list_1, until = time, wait = 1)
        time += 1
        key_pressed = cv2.waitKey(time_wait)
        # If "spacebar" is pressed, pause the video
        if key_pressed == ord(' ') or time == limit:
            cv2.waitKey(0)
        # If "left arrow" is pressed, go back frame_step frames
        elif key_pressed == ord('a'):
            print(f'A pressed, go back {frame_step} frames')
            if time >= frame_step:
                time -= frame_step
            else:
                time = 0
            cv2.waitKey(0)
        # If "right arrow" is pressed, go forward frame_step frames
        elif key_pressed == ord('d'):
            print(f'D pressed, go forward {frame_step} frames')
            if time <= limit - frame_step:
                time += frame_step
            else:
                time = limit
            cv2.waitKey(0)
        # If "up arrow" is pressed, increase frame_step by 10
        elif key_pressed == ord('w'):
            print(f'W pressed, increase frame_step by 10')
            if frame_step == 1:
                frame_step = 10
            else:
                frame_step += 10
        # If "down arrow" is pressed, decrease frame_step by 10
        elif key_pressed == ord('s'):
            print(f'S pressed, decrease frame_step by 10')
            if frame_step > 10:
                frame_step -= 10
            else:
                frame_step = 1 
        # If "q" is pressed, exit the video
        elif key_pressed == ord('q'):
            break

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type = str, default = 'single', help = 'single or multiple')
    parser.add_argument('-w', type = int, default = 10, help = 'time to wait between frames')
    parser.add_argument('-s', type = int, default = 0, help = 'time to start at')
    parser.add_argument('-f', type = int, default = 50, help = 'frame step')
    parser.add_argument('-t', type = int, default = 1, help = 'which tank is tracked (1-9)')

    args = parser.parse_args()

    main(mode = args.m, time_wait = args.w, time_start = args.s, frame_step = args.f, tracked_tank = args.t)
