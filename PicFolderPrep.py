from itertools import groupby
from operator import itemgetter
from functools import reduce
from multiprocessing import Pool, cpu_count, Manager, Process
import threading
from os import walk
import os
import json
import sys
import io
from PrepImage import PrepImage
import time
import random

def DebugPrint(debug, message):
    if debug:
        print(message)


class PicFolderPrep:
    folder_name = ""
    file_list = []
    rgb_info = {}

    # User should never call this method directly
    # this is a function definition for each thread's work
    def ProcessorWork(self, start_index, end_index, process_id, return_dict):
        start_time = time.time()
        # slice up the work
        rgb_dict = {}
        file_list_slice = self.file_list[start_index:end_index]
        for file in file_list_slice:
            p = PrepImage(file)  # prep image
            if (p.file_name != ""):  # if init is success
                p.PreProcess()
                if (p.image != None):  # if the size is good
                    rgb = p.GetColor()
                    if rgb in rgb_dict:
                        rgb_dict[rgb].append(file)
                    else:
                        rgb_dict[rgb] = [file]
        # define a dictionary for each process
        return_dict[process_id] = rgb_dict
        print("process %d finished --- %s seconds ---" %
              (process_id, time.time() - start_time))

    # input, the folder name
    # this will generate a list of files ready to be processed
    def __init__(self, folder_name):
        self.folder_name = folder_name
        file_list = []
        for (dirpath, _, filenames) in walk(folder_name):
            for f in filenames:
                if (f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))):
                    file_abs_path = os.path.abspath(os.path.join(dirpath, f))
                    file_list.append(file_abs_path)
        self.file_list = file_list

    # get the average rgb color of a photo for each file in the list
    # it will dump a json file, which the name will be user defined
    # since the process can be fairly slow, this is done using multi threading
    def GetColorList(self, info_name="color_info.json"):
        cpu_counts = cpu_count()
        print("Start work on %d process" % (cpu_counts))
        manager = Manager()
        return_dict = manager.dict()  # get a dictionary that can be used in multiprocessing

        jobs = []
        random.shuffle(self.file_list) # need to do that since there can be folder containing large files
        slice_size = int(len(self.file_list)/cpu_counts)+1
        for i in range(cpu_counts):
            p = Process(target=self.ProcessorWork, args=(
                slice_size*i, slice_size*(i+1), i, return_dict))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        for key in return_dict:
            for rgb in return_dict[key]:
                r = rgb[0]
                g = rgb[1]
                b = rgb[2]
                rgb_key = str(r)+"||"+str(g)+"||"+str(b)
                if rgb_key in self.rgb_info:
                    self.rgb_info[rgb_key] += return_dict[key][rgb]
                else:
                    self.rgb_info[rgb_key] = return_dict[key][rgb]
        
        # delete -1 -1 -1
        self.rgb_info.pop("-1||-1||-1", None)
        print("There are %d photos and %d unique colors" %
              (len(self.file_list), len(self.rgb_info)))
        with open(info_name, 'w') as outfile:
            json.dump(self.rgb_info, outfile)

