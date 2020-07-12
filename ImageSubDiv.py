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
from progress.bar import Bar

# This class subdivides an image to smaller squares
# based on user settings of largest block size and smallest block size
# at the beginning, user can also choose to enlarge the picture so that
# each square has larger pixel counts


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

    # input, file name and enlarge factor
    # enlarge factor is used to enlarge or shrink the photo
    # so that there are more pixel count
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
                im = cv2.imread(self.file_name)
            else:
                im = np.asarray(im)
            self.im = im
            # because they are bgr initially
            if if_converted:
                self.im = cv2.cvtColor(self.im, cv2.COLOR_BGR2RGB)
            self.all_blocks = []
            self.block_colors = []
            self.block_pic = []
        else:
            print("File extension not accepted %s" % (file_name))
            return

    # input, the largest and smallest block size
    # this method subdivides the picture based on gradient value
    # the gradient value represents color change internsity in the picture
    # the incentive is that you will want more blocks at the place where
    # color changes more drastically
    # and less blocks where the color stays constant
    def SubDiv(self, largest_block_size=50, smallest_block_size=1, alpha=0.6, use_gray_gradient=True):
        gradient = None
        if (use_gray_gradient):
            gray = cv2.cvtColor(self.im, cv2.COLOR_RGB2GRAY)  # the gray values
            blur = cv2.blur(gray, (5, 5))  # the blurred pic, in gray
            gradient = cv2.Laplacian(blur, cv2.CV_64F)  # the gradient map
            gradient = cv2.blur(gradient, (5, 5))  # the blurred pic, in gray
        else:
            input_r = self.im[:, :, 0]
            input_g = self.im[:, :, 1]
            input_b = self.im[:, :, 2]
            blur_r = cv2.blur(input_r, (5, 5))
            blur_g = cv2.blur(input_g, (5, 5))
            blur_b = cv2.blur(input_b, (5, 5))
            # the gradient map for r channel
            gradient_r = cv2.Laplacian(blur_r, cv2.CV_64F)
            # the gradient map for g channel
            gradient_g = cv2.Laplacian(blur_g, cv2.CV_64F)
            # the gradient map for b channel
            gradient_b = cv2.Laplacian(blur_b, cv2.CV_64F)
            gradient = gradient_r + gradient_g + gradient_b
            gradient = cv2.blur(gradient, (5, 5))

        width = gradient.shape[1]
        height = gradient.shape[0]
        width = width - width % largest_block_size  # because we don't want extras
        height = height - height % largest_block_size  # because we don't want extras
        height_block = int(height/largest_block_size)
        width_block = int(width/largest_block_size)
        self.width = width
        self.height = height
        print("Width %d, height %d" % (width, height))

        for i in range(height_block):
            for j in range(width_block):
                sdtree = SubDivTree((i*largest_block_size, j*largest_block_size),
                                    ((i+1)*largest_block_size, (j+1)*largest_block_size), smallest_block_size, gradient[i*largest_block_size:(i+1)*largest_block_size, j*largest_block_size:(j+1)*largest_block_size], alpha=alpha)
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
    # user need to input the json file generated by picfolderprep
    def ReadColorInfo(self, file_name="color_info.json"):
        unique_pic_count = 0
        with open(file_name, 'r') as f:
            colors = json.load(f)
            for key in colors:
                color_tuple = tuple([int(x) for x in key.split("||")])
                self.color_info[color_tuple] = colors[key]
                unique_pic_count += len(colors[key])
        print("There are %d unique colors and %d unique pictures" %
              (len(self.color_info), unique_pic_count))

    # for each color needed, find what color in color info list
    # can be a candidate to be used
    # this will be later be a default process
    def ProcessColors(self):
        color_info_existed_color = self.color_info.keys()
        index = list(range(len(self.block_colors)))
        # shuffle the index so that we access blocks randomly
        random.shuffle(index)
        self.block_pic = [""]*len(self.block_colors)
        picked_file_count = {}
        # how many times do we allow a picture to be repeatedly used
        repeated_count = int(
            max([5, 5*len(self.needed_color_count)/len(self.color_info)]))
        bar = Bar('Picking pictures', max=len(index))
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
            bar.next()
        print("\nPicture picking done, %d different pictures picked" %
              (len(picked_file_count)))

    # finally paste the pictures
    def PastePics(self, out_file="test_out.jpg"):
        index = list(range(len(self.block_colors)))
        # now we want to sort the index based on its picture
        index = sorted(index, key=lambda x: self.block_pic[x][0])
        # the new image in numpy array
        new_image_np = np.zeros((self.height, self.width, 3))
        file_dict = {}

        for ind in index:
            file_name = self.block_pic[ind][0]
            if file_name in file_dict:
                file_dict[file_name].append(ind)
            else:
                file_dict[file_name] = [ind]
        bar = Bar('Pasting pictures', max=len(index))
        for file_name in file_dict:
            file_color = self.block_pic[file_dict[file_name][0]][1]
            prepi = PrepImage(file_name)
            prepi.PreProcess(desired_size=-1)  # do not resize the image now
            size_dict = {}
            for ind in file_dict[file_name]:
                tl = self.all_blocks[ind][0]  # top left corner
                br = self.all_blocks[ind][1]  # bottom right corner
                size = br[0] - tl[0]
                if size in size_dict:
                    size_dict[size].append(ind)
                else:
                    size_dict[size] = [ind]

            for size in size_dict:
                resized_image = prepi.image.resize((size, size), Image.LANCZOS)
                resized_image_array = np.array(resized_image).astype(np.int16)
                for ind in size_dict[size]:
                    tl = self.all_blocks[ind][0]  # top left corner
                    br = self.all_blocks[ind][1]  # bottom right corner
                    dest_color = self.block_colors[ind]
                    prepi_np = np.copy(resized_image_array)
                    # add a color mask
                    prepi_np[:, :, 0] += int((dest_color[0] - file_color[0])/2)
                    prepi_np[:, :, 1] += int((dest_color[1] - file_color[1])/2)
                    prepi_np[:, :, 2] += int((dest_color[2] - file_color[2])/2)
                    new_image_np[tl[0]:br[0], tl[1]:br[1], :] = prepi_np
                    bar.next()

        # the final image needs to be clipped
        new_image_np = np.clip(new_image_np, a_min=0,
                               a_max=255).astype(dtype=np.uint16)
        new_image_np = cv2.cvtColor(new_image_np, cv2.COLOR_RGB2BGR)
        cv2.imwrite(out_file, new_image_np)
        print("\nPicture pasting done, saved at "+out_file)
        # new_image.save(out_file)
