import cv2
import os


def DebugPrint(debug, message):
    if debug:
        print(message)


class PrepVideo:
    file_name = ""  # the image file name
    video = None
    # width = 0
    # height = 0
    length = 0
    fps = 0

    def __init__(self, file_name):
        # try to load the file using cv2
        try:
            # it is possible that a image to be read
            # we will not exclude such cases
            video = cv2.VideoCapture(file_name)
            self.video = video
            self.file_name = file_name
            self.length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = int(video.get(cv2.CAP_PROP_FPS))
            print("Video %s has %d frames at an fps of %d" % (file_name, self.length, self.fps))
        except:
            return

    def SaveFrames(self, folder_name="out_frames", skip = 1):
        count = 0
        success, image = self.video.read()
        file_name_base = "".join(self.file_name.split(".")[:-1])
        if (not os.path.isdir(folder_name)):
            os.mkdir(folder_name)
        while success:
            if (count%skip == 0):
                cv2.imwrite("."+os.sep+folder_name+os.sep+file_name_base +
                            "_frame_"+str(count)+".jpg", image)
            success, image = self.video.read()
            count += 1
            if (count%100 == 0):
                print("%d/%d frames passed"%(count, self.length))
        print("%d/%d frames passed"%(self.length, self.length))

    # we will continue to use rgb


# test = PrepVideo("test.webm")
# test.SaveFrames(skip = 15)
