#                         .       .
#                        / `.   .' \
#                .---.  <    > <    >  .---.
#                |    \  \ - ~ ~ - /  /    |
#                 ~-..-~             ~-..-~
#             \~~~\.'                    `./~~~/
#   .-~~^-.    \__/                        \__/
# .'  O    \     /               /       \  \
#(_____,    `._.'               |         }  \/~~~/
# `----.          /       }     |        /    \__/
#       `-.      |       /      |       /      `. ,~~|
#           ~-.__|      /_ - ~ ^|      /- _      `..-'   f: f:
#                |     /        |     /     ~-.     `-. _||_||_
#                |_____|        |_____|         ~ - . _ _ _ _ _>
#


#imports--------
import sys
import os
from PIL import Image


#sysargs--------

cover_image = Image.open(sys.argv[1])

message_file = open(sys.argv[2], "r")

#check for data in msg file
if os.stat(sys.argv[2]).st_size == 0:
    sys.exit("message file empty")



#global init---------

#raw rgb data
global_pixel_data = cover_image.load()

# image y,x size
global_image_y_axis_value, global_image_x_axis_value = cover_image.size

#read first byte
global_unicode_value = message_file.read(1)

#embedded char counter
global_number_characters_embedded = 1

#num of char from message file
global_read_from_message_count = 0

# unicode --> int --> binary
global_binary_bitstring = bin(ord(global_unicode_value))[2:]

#block size
global_matrix_size_x = 2
global_matrix_size_y = 2

#eof flag
global_eof_flag = 0

# Qtable to classify pixels based on the difference in pixel value to the number of bits to be substituted
def quantizationTable(channel_difference):

    if channel_difference < 16:
        # if ___x ___[_]
        number_of_bits = 1

    elif 16 < channel_difference < 32:
        # if __x_ __[__]
        number_of_bits = 2

    else:
        # if xx__ _[___]
        number_of_bits = 3

    # #LSB to be substituted
    return number_of_bits

# no padding just embed
def embedBits(channel_difference, int_pixel_value):

    #global refs
    global global_binary_bitstring

    # init------
    #set to bitstring[] after rgb channel_difference
    global_binary_bitstring = global_binary_bitstring[channel_difference:]

    #rgb value set to bin then split
    binary_pixel_value = bin(int_pixel_value)[2:]

    #new bin rgb value
    new_binary_pixel_value = binary_pixel_value[: (len(binary_pixel_value) - len(global_binary_bitstring[:channel_difference]))] + global_binary_bitstring[:channel_difference]

    #new pixel value as int from base 2
    return int(new_binary_pixel_value, 2)


# if more bits needed that are in data to be embedded pad the bits
def padBits(channel_difference, int_pixel_value):

    #global refs
    global global_binary_bitstring, global_read_from_message_count, global_unicode_value, global_eof_flag, message_file, global_number_characters_embedded

    #init---------
    #add and reshape some 0 bits
    new_bitstring = global_binary_bitstring + "0000000"[: (channel_difference - len(global_binary_bitstring))]

    #new bin from rgb value
    binary_value = bin(int_pixel_value)[2:]

    #get new bin pixel value
    new_binary_value = binary_value[: (len(binary_value) - len(new_bitstring))] + new_bitstring

    # read new character
    global_unicode_value = message_file.read(1)
    global_read_from_message_count += 1

    #check message file does not have readable data
    if len(global_unicode_value) == 0:

        print("eof flag - chars embedded: " + str(global_number_characters_embedded))

        #close file and set eof flag
        message_file.close()
        global_eof_flag = 1

        # new pixel value as int from base 2
        return int(new_binary_value, 2)

    #check if more data unicode --> int --> bin
    global_binary_bitstring = bin(ord(global_unicode_value))[2:]

    # add to embedded character count and
    global_number_characters_embedded += 1

    #return new int pixel value from base 2 bin value
    return int(new_binary_value, 2)


# calculate embedding capacity of the given cover image
def embedCapacity():

    #init-------
    embedding_capacity = 0

    #same inner and outer loops in main()
    # split image into integer div number of matricies
    for image_y in range(0, global_image_y_axis_value // global_matrix_size_y * global_matrix_size_y, global_matrix_size_y):

        for image_x in range(0, global_image_x_axis_value // global_matrix_size_x * global_matrix_size_x, global_matrix_size_x):

            # get reference pixel values
            red_reference_pixel, green_reference_pixel, blue_reference_pixel = global_pixel_data[image_y + 1, image_x + 1]

            # forall pixels in the matrix
            for matrix_y in range(image_y, (image_y + 3)):

                if matrix_y >= global_image_y_axis_value:
                    # end of img end loop
                    break

                for matrix_x in range(image_x, (image_x + 3)):

                    if matrix_y == image_y + 1 and matrix_x == image_x + 1:
                        #end of row/col skip
                        continue

                    if matrix_x >= global_image_x_axis_value:
                        #end of img end loop
                        break

                    # rgb from mat y x
                    red_pixel, green_pixel, blue_pixel = global_pixel_data[matrix_y, matrix_x]

                    # pixel value differences in each of the rgb channels
                    red_pixel_difference = abs(red_pixel - red_reference_pixel)
                    green_pixel_difference = abs(green_pixel - green_reference_pixel)
                    blue_pixel_difference = abs(blue_pixel - blue_reference_pixel)

                    # calculate total capacity
                    embedding_capacity = (embedding_capacity + quantizationTable(red_pixel_difference) + quantizationTable(green_pixel_difference) + quantizationTable(blue_pixel_difference))

    return embedding_capacity


# Main Function
def main():

    #init counter
    embed_counter = 0

    #embed capacity
    print("cover image capacity: ", embedCapacity())

    #divide into global_matrix_size_x x global_matrix_size_y
    # 0 to ((image size // matrix size) * matrix size)  step: matrix size
    for imageY in range(0, global_image_y_axis_value // global_matrix_size_y * global_matrix_size_y, global_matrix_size_y):

        for imageX in range(0, global_image_x_axis_value // global_matrix_size_x * global_matrix_size_x, global_matrix_size_x):

            #get reference pixel values from pixel data mat[]
            red_reference_pixel, green_reference_pixel, blue_reference_pixel = global_pixel_data[imageY + 1, imageX + 1]

            # for all pixels in the matrix[ y x ]
            #row then column
            for matrix_y in range(imageY, (imageY + 3)):

                if matrix_y >= global_image_y_axis_value:
                    # end of img end loop
                    break

                for matrix_x in range(imageX, (imageX + 3)):

                    if matrix_y == imageY + 1 and matrix_x == imageX + 1:
                        # end of row/col skip
                        continue

                    if matrix_x >= global_image_x_axis_value:
                        # end of img end loop
                        break

                    #target pixel data from mat[ y x ]
                    target_red_pixel, target_green_pixel, target_blue_pixel = global_pixel_data[matrix_y, matrix_x]

                    # differences in each of the channels
                    red_pixel_difference = abs(target_red_pixel - red_reference_pixel)
                    green_pixel_difference = abs(target_green_pixel - green_reference_pixel)
                    blue_pixel_difference = abs(target_blue_pixel - blue_reference_pixel)

                    # until message file is eof by flag set in padBits()
                    #if quantTable(difference) #bits to sub < length of data to be embed then no padding
                    #else #bits to sub >= length of data to be embed then pad by reshape data
                    if global_eof_flag == 0:
                        if quantizationTable(red_pixel_difference) < len(global_binary_bitstring):
                            new_red_pixel = embedBits(quantizationTable(red_pixel_difference), target_red_pixel)
                        else:
                            new_red_pixel = padBits(quantizationTable(red_pixel_difference), target_red_pixel)

                    if global_eof_flag == 0:
                        if quantizationTable(green_pixel_difference) < len(global_binary_bitstring):
                            new_green_pixel = embedBits(quantizationTable(green_pixel_difference), target_green_pixel)
                        else:
                            new_green_pixel = padBits(quantizationTable(red_pixel_difference), target_red_pixel)

                    if global_eof_flag == 0:
                        if quantizationTable(blue_pixel_difference) < len(global_binary_bitstring):
                            new_blue_pixel = embedBits(quantizationTable(blue_pixel_difference), target_blue_pixel)
                        else:
                            new_blue_pixel = padBits(quantizationTable(red_pixel_difference), target_red_pixel)

                    #when message is eof
                    if global_eof_flag == 1:

                        #set new pixel values
                        global_pixel_data[matrix_y, matrix_x] = (new_red_pixel, new_green_pixel, new_blue_pixel)

                        #cover image write
                        cover_image.save("stego_obj_" + sys.argv[1])

                        #some stats?
                        print("number of bits embeded:", embed_counter)

                        sys.exit("qq")

                    #update # embdeded bits
                    embed_counter = (embed_counter + quantizationTable(red_pixel_difference) + quantizationTable(green_pixel_difference) + quantizationTable(blue_pixel_difference))

                    # set new pixel values in mat[y x]
                    global_pixel_data[matrix_y, matrix_x] = (new_red_pixel, new_green_pixel, new_blue_pixel)
    #check if message > capacity
    sys.exit("message > capacity")

if __name__ == "__main__":
    main()

