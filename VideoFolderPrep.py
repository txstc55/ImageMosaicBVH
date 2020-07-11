from PrepVideo import PrepVideo
from PicFolderPrep import PicFolderPrep
import cv2
import os
from os import walk
import time
from multiprocessing import Pool, cpu_count, Manager, Process
import random

# this class should almost be the same with
# picfolderprep class
# but with one extra step
# saving frames of all the videos to a folder
# then basically just calling picfolderprep
# on that folder


class VideoFolderPrep:
    folder_name = ""
    file_list = []
    rgb_info = {}
    save_folder_name = ""

    # User should never call this method directly
    # this is a function definition for each thread's work
    # we will save frames of a video
    def ProcessorWork(self, start_index, end_index, process_id, skip_frame=1, save_folder_name="out_frames"):
        start_time = time.time()
        # slice up the work
        file_list_slice = self.file_list[start_index:end_index]
        for file in file_list_slice:
            p = PrepVideo(file)  # prep image
            if (p.file_name != ""):  # if init is success
                p.SaveFrames(folder_name=save_folder_name, skip=skip_frame)
        print("process %d finished --- %s seconds ---" %
              (process_id, time.time() - start_time))

    # given a folder name, we will pick all the files that can be opened
    # as a video file, this will include pictures and maybe also gifs
    # since they are videos with only 1 frame
    def __init__(self, folder_name):
        self.folder_name = folder_name
        file_list = []
        for (dirpath, _, filenames) in walk(folder_name):
            for f in filenames:
                try:
                    file_abs_path = os.path.abspath(os.path.join(dirpath, f))
                    # just checking if we can open this as a video file
                    count = cv2.VideoCapture(file_abs_path).get(
                        cv2.CAP_PROP_FRAME_COUNT)
                    if (count):
                        file_list.append(file_abs_path)
                except:
                    pass  # we cannot process this file as a video
        # this will give us a list of files that can be opend by cv2 as a video
        self.file_list = file_list
        print(self.file_list)

    def SaveFramesParallel(self, skip_frame=1, save_folder_name="out_frames"):
        if (not os.path.isdir(save_folder_name)):
            os.mkdir(save_folder_name)
        self.save_folder_name = save_folder_name
        cpu_counts = cpu_count()
        print("Start work on %d process" % (cpu_counts))
        jobs = []
        # need to do that since there can be folder containing large files
        random.shuffle(self.file_list)
        slice_size = int(len(self.file_list)/cpu_counts)+1
        for i in range(cpu_counts):
            p = Process(target=self.ProcessorWork, args=(
                slice_size*i, slice_size*(i+1), i, skip_frame, save_folder_name))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
    
    def GetFrameColors(self, info_name="color_info.json"):
        folder = PicFolderPrep(self.save_folder_name)
        folder.GetColorList(info_name = info_name)

