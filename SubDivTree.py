import numpy as np
from math import ceil


def return_br_position(top_left, length):
    return(top_left[0]+length, top_left[1]+length)


def return_np_block(np_block, tl, length, top_left):
    relative_tl0 = tl[0] - top_left[0]
    relative_tl1 = tl[1] - top_left[1]
    return np_block[relative_tl0:relative_tl0+length, relative_tl1:relative_tl1+length]


# Normally the user should not call this class
# giving a matrix in numpy
# this method will subdivide the region whenever there is
# an element that is greater or equal to 1
# the entire block will than be multiplied by some factor
# so that it will not divide untill the block size is 1
# but user can also define the snallest block size
# so that it stops at a certain point
class SubDivTree:
    top_left_position = (0, 0)
    bot_right_position = (0, 0)
    smallest_block_size = 2
    sub_block = []

    # where is this segmentation of image at
    # how much do we divide for each iteration of subdivision

    def __init__(self, top_left_position, bot_right_position, smallest_block_size, np_block):
        self.top_left_position = top_left_position
        self.bot_right_position = bot_right_position
        square_width = np_block.shape[0]  # how large is this block
        divided_square_width = int(ceil(square_width/2.0))
        # print(top_left_position)
        # print(bot_right_position)
        # do a subdivision if there is a gradient value inside the block
        if (np_block.max() >= 1 and np_block.shape[0] >= 2 * smallest_block_size):
            # print(np_block)
            np_block *= 0.6
            # top left, the top left position of square 1
            tl = top_left_position
            # top middle, the top left position of square 2
            tm = (top_left_position[0],
                  top_left_position[1] + int(square_width/2))
            # middle top, the top left position of square 3
            ml = (top_left_position[0] + int(square_width/2),
                  top_left_position[1])
            # middle middle, the top left position of square 4
            mm = (top_left_position[0] + int(square_width/2),
                  top_left_position[1] + int(square_width/2))
            # add the new four blocks
            sub_block = []
            tl_block = SubDivTree(tl, return_br_position(tl, divided_square_width), smallest_block_size,
                                  return_np_block(np_block, tl, divided_square_width, top_left_position))
            sub_block.append(tl_block)
            tm_block = SubDivTree(tm, return_br_position(tm, divided_square_width), smallest_block_size,
                                  return_np_block(np_block, tm, divided_square_width, top_left_position))
            sub_block.append(tm_block)
            ml_block = SubDivTree(ml, return_br_position(ml, divided_square_width), smallest_block_size,
                                  return_np_block(np_block, ml, divided_square_width, top_left_position))
            sub_block.append(ml_block)
            mm_block = SubDivTree(mm, return_br_position(mm, divided_square_width), smallest_block_size,
                                  return_np_block(np_block, mm, divided_square_width, top_left_position))
            sub_block.append(mm_block)
            self.sub_block = sub_block
        # print(len(self.sub_block), top_left_position, bot_right_position)

    def ExtractBlock(self):
        if (len(self.sub_block) == 0):
            return[(self.top_left_position, self.bot_right_position)]
        else:
            all_blocks = []
            block_queue = self.sub_block
            # print(len(self.sub_block))
            while(len(block_queue) != 0):
                # print(len(block_queue))
                block = block_queue.pop(0)
                # print(len(block_queue))
                if (len(block.sub_block) == 0):
                    all_blocks.append(
                        (block.top_left_position, block.bot_right_position))
                else:
                    block_queue += block.sub_block
            return all_blocks

