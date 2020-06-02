from PIL import Image
from PIL import ImageFilter
import numpy as np
import cv2
from math import atan2
from math import log2
from SubDivTree import SubDivTree
from PrepImage import convert_to_srgb
import time
import json
import random
from PrepImage import PrepImage


class ImageSubDiv:
    file_name = ""
    im = None
    division_amount = 0
    all_blocks = None
    block_colors = None
    block_pic = None
    color_info = {}
    needed_color_count = {}
    width = 0
    height = 0

    def __init__(self, file_name, enlarge=1):
        # check if it is an image file by just looking at the extension
        if (file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))):
            self.file_name = file_name
            im = Image.open(file_name)
            width, height = im.size
            # upscale the image if requested
            if (enlarge > 1):
                im = im.resize((width*enlarge, height*enlarge), Image.LANCZOS)
            im, if_converted = convert_to_srgb(im)
            if if_converted:
                new_pic_file_name = file_name.split(
                    ".")[0]+"_removed_profile."+file_name.split(".")[-1]
                print("Picture has color profile, removed profile and saved to %s" % (
                    new_pic_file_name))
                im.save(new_pic_file_name)
                self.file_name = new_pic_file_name
            self.im = cv2.imread(self.file_name)
            # because they are bgr initially
            self.im = cv2.cvtColor(self.im, cv2.COLOR_BGR2RGB)
            self.all_blocks = []
            self.block_colors = []
            self.block_pic = []
        else:
            print("File extension not accepted %s" % (file_name))
            return

    def SubDiv(self, largest_block_size=50, smallest_block_size=1):
        gray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)  # the gray values
        blur = cv2.blur(gray, (5, 5))  # the blurred pic, in gray

        gradient = cv2.Laplacian(blur, cv2.CV_64F)  # the gradient map
        gradient = cv2.blur(gradient, (5, 5))  # the blurred pic, in gray
        # gradient /= 4
        width = gray.shape[1]
        height = gray.shape[0]
        width = width - width % largest_block_size  # because we don't want extras
        height = height - height % largest_block_size  # because we don't want extras
        height_block = int(height/largest_block_size)
        width_block = int(width/largest_block_size)
        self.width = width
        self.height = height

        for i in range(height_block):
            for j in range(width_block):
                sdtree = SubDivTree((i*largest_block_size, j*largest_block_size),
                                    ((i+1)*largest_block_size, (j+1)*largest_block_size), smallest_block_size, gradient[i*largest_block_size:(i+1)*largest_block_size, j*largest_block_size:(j+1)*largest_block_size])
                self.all_blocks += sdtree.ExtractBlock()
        # get all the color needed for this image
        for block in self.all_blocks:
            tl = block[0]
            br = block[1]
            r = self.im[tl[0]:br[0], tl[1]:br[1], 0]
            g = self.im[tl[0]:br[0], tl[1]:br[1], 1]
            b = self.im[tl[0]:br[0], tl[1]:br[1], 2]
            rgb = (int(r.mean()), int(g.mean()), int(b.mean()))
            if (rgb in self.needed_color_count):
                self.needed_color_count[rgb] += 1
            else:
                self.needed_color_count[rgb] = 1
            self.block_colors.append(rgb)

        print("There are %d blocks and %d different colors" %
              (len(self.all_blocks), len(self.needed_color_count)))

    # read a color info file
    def ReadColorInfo(self, file_name="color_info.json"):
        with open(file_name, 'r') as f:
            colors = json.load(f)
            for key in colors:
                color_tuple = tuple([int(x) for x in key.split("||")])
                self.color_info[color_tuple] = colors[key]
        print("There are %d unique colors" % (len(self.color_info)))

    # for each color needed, find what color in color info list
    # can be a candidate to be used
    def ProcessColors(self):
        color_info_existed_color = self.color_info.keys()
        index = list(range(len(self.block_colors)))
        # shuffle the index so that we access blocks randomly
        random.shuffle(index)
        self.block_pic = [""]*len(self.block_colors)
        picked_file_count = {}
        # how many times do we allow a picture to be repeatedly used
        repeated_count = int(
            max([10, 10*len(self.needed_color_count)/len(self.color_info)]))
        count = 0
        for ind in index:
            color = self.block_colors[ind]  # get the color
            color_difference = [(((x[0]-color[0])**2 + (x[1]-color[1]) **
                                  2 + (x[2]-color[2])**2), x) for x in color_info_existed_color]
            # get the color difference, and sort them according to the distance between the color
            color_difference = sorted(color_difference, key=lambda x: x[0])
            picked_color = random.choices(population=[x[1] for x in color_difference], weights=[
                                          1.0/(x[0]+1) for x in color_difference], k=1)[0]
            picked_file_name = random.choice(self.color_info[picked_color])
            it = 0
            while it < 200:
                if picked_file_name not in picked_file_count:
                    self.block_pic[ind] = (picked_file_name, picked_color)
                    picked_file_count[picked_file_name] = 1
                    break
                else:
                    if picked_file_count[picked_file_name] <= repeated_count:
                        self.block_pic[ind] = (picked_file_name, picked_color)
                        picked_file_count[picked_file_name] += 1
                        break
                    else:
                        picked_color = random.choices(population=[x[1] for x in color_difference], weights=[
                            1.0/(x[0]+1) for x in color_difference], k=1)[0]
                        picked_file_name = random.choice(
                            self.color_info[picked_color])
                        it += 1
                        if (it == 100):  # give up
                            self.block_pic[ind] = (
                                picked_file_name, picked_color)
            count += 1
            if (count % 1000 == 0):
                print("Picture picking progress : %d/%d" % (count, len(index)))
        print("Picture picking done")

    # finally paste the pictures
    def PastePics(self):
        index = list(range(len(self.block_colors)))
        # shuffle the index so that we access blocks randomly
        random.shuffle(index)
        new_image = Image.new("RGB", (self.width, self.height))
        # new_image.paste(Image.fromarray(self.im), (0, 0))
        count = 0
        for ind in index:
            file_name = self.block_pic[ind][0]
            # print(file_name)
            file_color = self.block_pic[ind][1]
            dest_color = self.block_colors[ind]
            prepi = PrepImage(file_name)
            tl = self.all_blocks[ind][0]
            br = self.all_blocks[ind][1]
            # print((br[0] - tl[0]))
            prepi.PreProcess(desired_size=(br[0] - tl[0]))
            prepi_np = np.array(prepi.image).astype(np.int16)
            # add a color mask
            prepi_np[:, :, 0] += int((dest_color[0] - file_color[0])/2)
            prepi_np[:, :, 1] += int((dest_color[1] - file_color[1])/2)
            prepi_np[:, :, 2] += int((dest_color[2] - file_color[2])/2)
            prepi_np = np.clip(prepi_np, a_min=0, a_max=255)
            prepi.image = Image.fromarray(prepi_np.astype(np.uint8))
            new_image.paste(prepi.image, (tl[1], tl[0]))
            count += 1
            if (count % 1000 == 0):
                print("Picture pasting progress : %d/%d" % (count, len(index)))
        print("Picture pasting done")
        new_image.save("test_out.jpg")


# test = ImageSubDiv("corgi.jpg", enlarge=2)
# test.SubDiv(largest_block_size=500, smallest_block_size=1)
# test.ReadColorInfo()
# test.ProcessColors()
# test.PastePics()
# print(test.im.shape)
