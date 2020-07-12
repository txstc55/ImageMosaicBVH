# ImageMosaicBVH

Yet, another library to do image mosaic. This is an attempt to make one of my old project [Image Assembling](https://github.com/txstc55/image_assembling) a better one. And indeed, I am very satisfied with the result.

## What's the difference
While many of the current libraries produces an image that contains sub-images of the same size which cuts some fine detail of the original image, and presents large repetition of a subset of images which makes it horrible to look at when zoom in, this projects uses a subdivision technique to preserve more detail at places where color change drastically and balance the repetition of input images.

To eliminate repeatedly using the same image on similar color blocks, this project also choose images not only based on color, but also how many times it has been chosen. The more it has been chosen before, the probability of choosing it again lowers, until it hits a limit and will never be chosen again.

This alone will make the image ugly since we don't always pick the best picture for a color. Hence, a mask is applied to each sub-image to match the color of that block.

## Prerequisite

There are a couple of libraries you need to install manually, or rely on main.py to install for you(a install will be invoked at the beginning of script if the library is not found):

CV2, for image processing

```bash
pip install opencv-python
```

Numpy, just because

```bash
pip install numpy
```

Pillow, which is also used for image processing

```bash
pip install Pillow
```

Then progressbar is also needed because it is fancy:

```bash
pip install progress
```

## How to run

Just do this:
```bash
python main.py
```

There is an interface that should guide you through all the trouble to generate an image. A typical run will be attached at the end for you to go through.

Note that this project is done with python 3 so maybe it has things that python 2 does not support. If you are still using python 2, JUST GO GET PYTHON 3, WHAT IS SO HARD ABOUT IT?


## Exactly what does it look like

Take for example, this image:

![An image I took](https://github.com/txstc55/ImageMosaicBVH/blob/master/showcase/test.jpg?raw=false)

We can see the color at the border of ipad changes drastically, so does the demon eye of the dog. With a general mosaic algorithm, those features a most likely lost. But look at the picture generated:

![Generated Mosaic](https://github.com/txstc55/ImageMosaicBVH/blob/master/showcase/test_out.jpg?raw=false)

Not only you can see a good transition from the background to the border of ipad, the flare of the demon eye is also well preserved.

Furthermore, if we zoom in on the border:

![Screenshot around border](https://github.com/txstc55/ImageMosaicBVH/blob/master/showcase/border.png?raw=false)

The images are smaller around places where color changes due to the subdivision technique.

To generate this picture, I used all my pictures, which has a total count of 1711, and 1680 of them are presented in this photo. As a result, you cannot spot two photos directly by just looking at it.

Technically you can view all my photos by just looking at this one example. Please don't, just don't be that creepy.

## For those who does not care about the performance

When you are analyzing a picture folder or video folder, since it is done with multi threading, you will feel laggy watching video or doing other things, but this should only take a small amout of time.

Once it starts to generate the image, it goes back to using single thread. This process will take some time depend on your input, but just leave it there and trust it to produce a good result.

## For those who cares about the performance

Generating the color information is fairly easy since it is done by multithreading. Picking the corresponding picture is done with single thread since it is probability-based, but is also fairly fast.

The slowest part is to paste the image. Oh boy, to generate this image it took me around 23 minutes in total (including pre-processing)

Why is it slow? Well because python's shared data is not that good. For all the shared data type, not only is slow, as f@#k, but also puts a limit on the size of file the pipe can transfer.

I tried to do pasting work on multithreading, then merge the photo using a shared queue, and whenever the queue is not empty, the master thread takes the object and do a merge. But like I mentioned, the size limit is just ruining everything, and when the imaage get larger, the get() operation just takes forever and beats the purpose of multithreading.

Essentially, this is a lot faster than the very first version I wrote. If you have better idea on speeding it up, don't hesitate and just open an issue or a pull request.

## But why?
I wanted to compress a whole porn into one image, that's why.

And now I can.

## A typical run

All the ***italic bold characters*** are the input

```
Welcome to use this library. This library aims to produce an image mosaic that preserves detail and tries to use all the images provided. Good luck have fun!
Please choose from the following options:
1. Prepare an image folder for generation, all images in subfolders will be included
2. Prepare a video folder for generation, all videos in subfolders will be included
3. Generate an image mosaic
4. Exit
```

Here we input ***1*** to first analyze a picture folder
```
You have chosen to prepare a picture folder. Pictures in this folder will be analyzed for color information, which can be used later on for assembling an image.
Please enter the picture folder path, all subfolders will be included for processing, press enter to go back to main menu.
```

Now we input the folder name, for this example we use the photo library: ***/Users/MyUserName/Pictures/Photos Library.photoslibrary/originals***
```
Pleae enter a name for json file. This json file contains necessary color information for assembling the final image. Press enter for default name: color_info.json.
```

Then we pick a name for the output json name, after that, pre process is ran on multi thread, here we use ***my_pictures.json***
```
Start work on 16 process
process 13 finished --- 59.92822599411011 seconds ---
process 15 finished --- 60.414633989334106 seconds ---
process 0 finished --- 63.85002422332764 seconds ---
process 9 finished --- 64.32532787322998 seconds ---
process 3 finished --- 65.41515588760376 seconds ---
process 5 finished --- 65.81360101699829 seconds ---
process 12 finished --- 67.81327104568481 seconds ---
process 6 finished --- 68.14862823486328 seconds ---
process 14 finished --- 68.49922609329224 seconds ---
process 2 finished --- 68.5216977596283 seconds ---
process 1 finished --- 68.62598705291748 seconds ---
process 10 finished --- 69.74604916572571 seconds ---
process 7 finished --- 69.77347493171692 seconds ---
process 8 finished --- 70.35482096672058 seconds ---
process 4 finished --- 71.23905110359192 seconds ---
process 11 finished --- 72.45990085601807 seconds ---
There are 1715 photos and 1689 unique colors
Color information saved in my_pictures.json
```

After that, you will be back at the main menu
```
Please choose from the following options:
1. Prepare an image folder for generation, all images in subfolders will be included
2. Prepare a video folder for generation, all videos in subfolders will be included
3. Generate an image mosaic
4. Exit
```

This time, we want to choose ***3*** for generation
```
You have chosen to generate an image mosaic. At this step you need color info generated from a picture folder or video folder to proceed.
Please enter a picture for generating image mosaic. Press enter to go back to main menu.
```

Input the picture you want to use, here we use ***test.jpg***
```
If you want to enlarge the picture, please enter a positive integer. Press enter for default of 1(do not enlarge it).
```

For this run, we do not want to change the image size so input ***1***
```
For every block in the final image, it shall be within a range of size you prefer. Each block will be subdivided into 4 smaller blocks evenly if necessary for better detail.

Please enter the largest block size.
```

We will set ***200*** for the largest block size
```
Please enter the smallest block size.
```

We will set ***100*** for the smallest block size

```
The frequency of how a block is divided is determined by the gradient value(based on image) and also an alpha value. The larger alpha, the more frequent blocks will be divided.
Please enter an alpha value between 0 and 1 exclusive.
```

Here, we choose ***0.5*** for the alpha value. The larger alpha is, the more subdivision will happen.

```
Width 4600, height 6000
There are 2619 blocks and 1297 different colors
Now the image is subdivided into color blocks, we will need a color info json to proceed.

Please enter the color info json file name to proceed. Press enter to go back to main menu
```

Previously we have saved the json file ***my_pictures.json***, we will use it here
```
There are 1689 unique colors and 1712 unique pictures
Picking pictures |################################| 2619/2619
Picture picking done, 1105 different pictures picked
Please enter the output file name. Press enter for default out.jpg.
```
We will save to ***out_test.jpg***
```
Pasting pictures |################################| 2619/2619
Picture pasting done, saved at out_test.jpg
Please choose from the following options:
1. Prepare an image folder for generation, all images in subfolders will be included
2. Prepare a video folder for generation, all videos in subfolders will be included
3. Generate an image mosaic
4. Exit
```

Finally, enter ***0*** to exit the program
