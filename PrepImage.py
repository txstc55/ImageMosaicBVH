import numpy as np
from PIL import Image
from PIL import ImageFilter
from PIL import ImageCms
import math
import PIL.ExifTags as ExifTags
import io


def DebugPrint(debug, message):
    if debug:
        print(message)


def convert_to_srgb(img):
    '''Convert PIL image to sRGB color space (if possible)'''
    # ok there might be a problem using this function
    # to solve it, completely remove PIL and Pillow package
    # then reinstall it using pip or conda or whatever
    # this is a pretty shitty problem
    # and there is no other solution other than this
    icc = img.info.get('icc_profile', '')
    if_changed = False
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
        if_changed = True
    return img, if_changed


class PrepImage:
    file_name = ""  # the image file name
    image = None
    width = 0
    height = 0

    def __init__(self, file_name):
        # check if it is an image file by just looking at the extension
        if (file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))):
            self.file_name = file_name
        else:
            return

    def PreProcess(self, debug=False, save_path=None, desired_size=0):
        if (self.file_name == ""):
            return  # just incase there is no protect against invalid files
        im = Image.open(self.file_name)
        width, height = im.size  # get the dimension
        if (width/height > 3 or height/width > 3):  # we dont want to handle this aspect ratio
            return

        # crop the image
        if width > height:
            im = im.crop(((width-height)/2, 0, width -
                          (width-height)/2, height))
            width = height
        elif height > width:
            im = im.crop((0, (height-width)/2, width,
                          height - (height-width)/2))
            height = width
        else:
            pass

        # if we have a desired image size for the middle part
        if (desired_size > 0):
            im = im.resize((desired_size, desired_size), Image.LANCZOS)
            self.width = desired_size
            self.height = desired_size
        else:
            # we want to resize the image to a reasonable small one
            # so that we dont work too hard on an image that will get small eventually
            # when we put it on mosaic
            while width > 1000 or height > 1000:
                width /= 2
                height /= 2
            width = int(width)
            height = int(height)
            width = width - width % 100  # always shrink the dimension to leave out some borders
            height = height - height % 100
            # resize the image to a smaller one
            im = im.resize((width, height), Image.LANCZOS)
            # im = im.filter(ImageFilter.GaussianBlur(radius=2))  # blur the image
            # we only want the center piece
            self.width = width  # because we only want the square image
            self.height = height  # because we only want the square image

        orient = -1  # the orientation of the image
        try:
            exif = dict((ExifTags.TAGS[k], v) for k, v in im._getexif(
            ).items() if k in ExifTags.TAGS)
            orient = exif["Orientation"]  # get the orientation of the image
        except:
            pass

        # now rotate the image
        if orient == 3:
            im = im.rotate(180, expand=True)
        elif orient == 6:
            im = im.rotate(270, expand=True)
        elif orient == 8:
            im = im.rotate(90, expand=True)

        im, _ = convert_to_srgb(im)  # convert the color space to RGB
        im = im.convert("RGB")
        self.image = im  # save the image object to self now

        if save_path != None:
            im.save(save_path)

    # we will continue to use rgb
    def GetColor(self):
        colors = self.image.getcolors(self.width*self.height)
        r = 0
        g = 0
        b = 0
        try:
            for item in colors:
                rgb = item[1]
                r += rgb[0]*item[0]
                g += rgb[1]*item[0]
                b += rgb[2]*item[0]
            r /= self.width*self.height
            g /= self.width*self.height
            b /= self.width*self.height
            return (int(r), int(g), int(b))
        except:
            return(-1, -1, -1)


# if __name__ == "__main__":
#     test = PrepImage("test.jpg")
#     test.PreProcess(debug=True, save_path="test_out.jpg")
#     print(test.GetColor())
