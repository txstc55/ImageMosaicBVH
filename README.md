# ImageMosaicBVH

Yet, another library to do image mosaic. This is an attempt to make one of my old project [Image Assembling](https://github.com/txstc55/image_assembling) a better one. And indeed, I am very satisfied with the result.

## What's the difference
While many of the current libraries produces an image that contains sub-images of the same size which cuts some fine detail of the original image, and presents large repetition of a subset of images which makes it horrible to look at when zoom in, this projects uses a subdivision technique to preserve more detail at places where color change drastically and balance the repetition of input images.

To eliminate repeatedly using the same image on similar color blocks, this project also choose images not only based on color, but also how many times it has been chosen. The more it has been chosen before, the probability of choosing it again lowers, until it hits a limit and will never be chosen again.

This alone will make the image ugly since we don't always pick the best picture for a color. Hence, a mask is applied to each sub-image to match the color of that block.

## Prerequisite

There are a couple of libraries you need to install: CV2, which you can install by conda or pip:

```bash
pip install opencv-python
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

There is an interface that should guide you through all the trouble to generate an image

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