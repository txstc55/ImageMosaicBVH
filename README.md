# ImageMosaicBVH

Yet, another library to do image mosaic. This is an attempt to make one of my old project [Image Assembling](https://github.com/txstc55/image_assembling) a better one. And indeed, I am very satisfied with the result.

## What's the difference
While many of the current libraries produces an image that contains same size for all sub-images, and presents large repetition of some images, this projects uses a subdivision technique to preserve more detail at places where color change drastically.

To eliminate repeatedly using the same image on similar color blocks, this project also choose images not only based on color, but also how many times it has been chosen. The more it has been chosen before, the probability of choosing it again lowers, until it hits a limit and will never be chosen again.

This alone will make the image ugly since we don't always pick the best picture for a color. Hence, a mask is applied to each sub-image to match the color of that block.

## Exactly what does it look like

Take for example, this image:

![An image I took](https://github.com/txstc55/ImageMosaicBVH/blob/master/test.jpg?raw=false)

We can see the color at the border changes drastically, so does the demon eye of the dog. With a general mosaic algorithm, those features a most likely lost. But look at the picture generated:

![Generated Mosaic](https://github.com/txstc55/ImageMosaicBVH/blob/master/test_out.jpg?raw=false)