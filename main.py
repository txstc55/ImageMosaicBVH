from pip._internal import main
def import_or_install(package, package_name):
    try:
        __import__(package)
    except ImportError:
        print("%s not found, installing %s"%(package, package_name))
        main(['install', package_name])    

import_or_install("progress", "progress")
import_or_install("PIL", "Pillow")
import_or_install("numpy", "numpy")
import_or_install("cv2", "opencv-python")

from ImageSubDiv import ImageSubDiv
from PicFolderPrep import PicFolderPrep
from VideoFolderPrep import VideoFolderPrep
import os


def PreparePicFolder():
    print("You have chosen to prepare a picture folder. Pictures in this folder will be analyzed for color information, which can be used later on for assembling an image.")
    pic_folder = input(
        "Please enter the picture folder path, all subfolders will be included for processing, press enter to go back to main menu.\n")
    while (not os.path.isdir(pic_folder)):
        if (pic_folder == ""):
            return
        pic_folder = input(
            "Input folder does not exist, please enter a valid path, press enter to go back to main menu.\n")
    pic_folder_prep = PicFolderPrep(pic_folder)
    saved_color_file_name = input(
        "Pleae enter a name for json file. This json file contains necessary color information for assembling the final image. Press enter for default name: color_info.json.\n")
    if (saved_color_file_name == ""):
        saved_color_file_name = "color_info.json"
    pic_folder_prep.GetColorList(info_name=saved_color_file_name)
    print("Color information saved in "+saved_color_file_name)


def PrepareVideoFolder():
    print("You have chosen to prepare a video folder. Screenshots of all the videos in this folder will be saved and analyzed for color information, which can be used later on for assembling an image.")
    vid_folder = input(
        "Please enter the video folder path, all subfolders will be included for processing, press enter to go back to main menu.\n")
    while (not os.path.isdir(vid_folder)):
        if (vid_folder == ""):
            return
        vid_folder = input(
            "Input folder does not exist, please enter a valid path, press enter to go back to main menu.\n")
    vid_folder_prep = VideoFolderPrep(vid_folder)
    print("Normal video has around 30 frames per second. You can choose to skip a certain number of frames each time a screenshot is taken. 1 indicates every frame is saved, 10 indicates every 10th frame is saved.")
    skip_frame = input(
        "How many frames would you like to skip. Press enter for default of 5.\n")
    while (not skip_frame.isnumeric() or int(skip_frame) <= 0):
        if (skip_frame == ""):
            skip_frame = 5
            break
        skip_frame = input(
            "Please enter a positive integer or press enter for default of 5.\n")
    skip_frame = int(skip_frame)
    save_frame_folder = input(
        "The screenshots will be saved into a folder, please enter a folder name.\n")
    vid_folder_prep.SaveFramesParallel(
        skip_frame=skip_frame, save_folder_name=save_frame_folder)

    saved_color_file_name = input(
        "Pleae enter a name for json file. This json file contains necessary color information for assembling the final image. Press enter for default name: color_info.json.\n")
    if (saved_color_file_name == ""):
        saved_color_file_name = "color_info.json"
    vid_folder_prep.GetFrameColors(info_name=saved_color_file_name)


def PrepareMosaic():
    print("You have chosen to generate an image mosaic. At this step you need color info generated from a picture folder or video folder to proceed.")
    image_mosaic = None
    while True:
        pic_file = input(
            "Please enter a picture for generating image mosaic. Press enter to go back to main menu.\n")
        if pic_file == "":
            return

        enlarge_size = input(
            "If you want to enlarge the picture, please enter a positive integer. Press enter for default of 1(do not enlarge it).\n")
        while (not enlarge_size.isnumeric() or int(enlarge_size) <= 0):
            if (enlarge_size == ""):
                enlarge_size = 1
                break
            enlarge_size = input(
                "Please enter a positive integer or press enter for default of 1.\n")
        enlarge_size = int(enlarge_size)

        image_mosaic = ImageSubDiv(pic_file, enlarge=enlarge_size)
        if (image_mosaic.file_name != ""):
            break

    print("For every block in the final image, it shall be within a range of size you prefer. Each block will be subdivided into 4 smaller blocks evenly if necessary for better detail.\n")
    largest_block_size = None
    smallest_block_size = None
    while True:
        largest_block_size = input("Please enter the largest block size.\n")
        while (not largest_block_size.isnumeric() or int(largest_block_size) <= 0):
            if (largest_block_size == ""):
                largest_block_size = 1
                break
            largest_block_size = input(
                "Please enter a positive integer.\n")
        largest_block_size = int(largest_block_size)

        smallest_block_size = input("Please enter the smallest block size.\n")
        while (not smallest_block_size.isnumeric() or int(smallest_block_size) <= 0):
            if (smallest_block_size == ""):
                smallest_block_size = 1
                break
            smallest_block_size = input(
                "Please enter a positive integer.\n")
        smallest_block_size = int(smallest_block_size)

        if (largest_block_size <= smallest_block_size):
            print("Largest block size should be greater than the smallest block size")
        else:
            break

    print("The frequency of how a block is divided is determined by the gradient value(based on image) and also an alpha value. The larger alpha, the more frequent blocks will be divided.")
    alpha = None
    while True:
        alpha = input(
            "Please enter an alpha value between 0 and 1 exclusive.\n")
        try:
            alpha = float(alpha)
            if (alpha > 0 and alpha < 1):
                break
        except:
            pass
    image_mosaic.SubDiv(largest_block_size=largest_block_size,
                        smallest_block_size=smallest_block_size, alpha=alpha)

    print("Now the image is subdivided into color blocks, we will need a color info json to proceed.\n")

    while True:
        color_info = input(
            "Please enter the color info json file name to proceed. Press enter to go back to main menu\n")
        if color_info == "":
            return
        try:
            image_mosaic.ReadColorInfo(file_name=color_info)
            image_mosaic.ProcessColors()
            break
        except:
            print("Color info is not the correct format.")
            pass

    out_name = input(
        "Please enter the output file name. Press enter for default out.jpg.\n")
    if out_name == "":
        out_name = "out.jpg"
    image_mosaic.PastePics(out_file=out_name)


def MainMenu():
    while True:
        prompt_text = "Please choose from the following options:\n"
        initial_choice_list = [
            "1. Prepare an image folder for generation, all images in subfolders will be included\n",
            "2. Prepare a video folder for generation, all videos in subfolders will be included\n",
            "3. Generate an image mosaic\n",
            "0. Exit\n"
        ]
        initial_choice = input(prompt_text+"".join(initial_choice_list))
        if initial_choice.strip() == "1":
            PreparePicFolder()
        elif initial_choice.strip() == "2":
            PrepareVideoFolder()
        elif initial_choice.strip() == "3":
            PrepareMosaic()
        elif initial_choice.strip() == "0":
            return
        else:
            pass


if __name__ == "__main__":
    welcome_text = "Welcome to use this library. This library aims to produce an image mosaic that preserves detail and tries to use all the images provided. Good luck have fun!"
    print(welcome_text)
    MainMenu()
