import sys
import os
from PIL import Image

global_encode_decode_flag = sys.argv[1]

if global_encode_decode_flag == 'e':
    if os.stat(sys.argv[3]).st_size == 0:
        # check for data in msg file
        sys.exit("message file empty")

    cover_image = Image.open(sys.argv[2])
    message_file = open(sys.argv[3], "r")
    global_embed_counter = 0
    global_rgb_data = cover_image.load()
    global_image_height, global_image_width = cover_image.size
    temp_utf_string = message_file.read()
    global_binary_payload = ''.join('{0:08b}'.format(ord(x), 'b') for x in temp_utf_string)
    print(global_binary_payload)

    global_payload_size = len(global_binary_payload)
    binary_payload_size_32 = bin(global_payload_size)[2:].zfill(32)
    print(binary_payload_size_32)
    global_binary_payload = binary_payload_size_32 + global_binary_payload
    print(global_binary_payload)
    #n = int(global_binary_payload, 2)
    #print(n.to_bytes((n.bit_length() + 7) // 8, 'big').decode())
    global_payload_size = len(global_binary_payload)
    message_file.close()

elif global_encode_decode_flag == 'd':
    stego_image = Image.open(sys.argv[2])
    # secret_file = open(sys.argv[3], "w")
    global_rgb_data = stego_image.load()
    global_image_height, global_image_width = stego_image.size
    global_binary_secret = ''

else:
    sys.exit("unknown value")


# wu tsai ranges
def quantizationTable(channel_difference):
    if channel_difference <= 16:
        # if ___x ___[_]
        number_of_bits = 0

    elif 16 < channel_difference <= 32:
        # if __x_ __[__]
        number_of_bits = 1

    else:
        # if xx__ _[___]
        number_of_bits = 2

    # #LSB to be substituted
    return number_of_bits


def capacity():
    embedding_capacity = 0
    for image_y in range(0, global_image_height):
        for image_x in range(0, global_image_width, 2):
            if image_x + 1 == global_image_width:
                break

            #print(image_x, image_y)
            tuple = global_rgb_data[image_y, image_x]

            red_reference_pixel, green_reference_pixel, blue_reference_pixel = tuple[0], tuple[1], tuple[2]

            tuple = global_rgb_data[image_y, image_x + 1]
            red_pixel, green_pixel, blue_pixel = tuple[0], tuple[1], tuple[2]

            red_pixel_difference = abs(red_pixel - red_reference_pixel)
            green_pixel_difference = abs(green_pixel - green_reference_pixel)
            blue_pixel_difference = abs(blue_pixel - blue_reference_pixel)

            embedding_capacity = (embedding_capacity + quantizationTable(red_pixel_difference) + quantizationTable(
                green_pixel_difference) + quantizationTable(blue_pixel_difference))
    print(embedding_capacity)
    return embedding_capacity


def embedBits(channel_difference, int_reference_pixel_value, int_pixel_value):
    global global_binary_payload, global_embed_counter

    #print(global_binary_payload)
    binary_pixel_value = bin(int_reference_pixel_value)[2:].zfill(8)
    bits_to_embed = global_binary_payload[:channel_difference]

    #print("binpixval ", binary_pixel_value, "bitstoembed ", bits_to_embed)
    new_binary_pixel_value = binary_pixel_value[:len(binary_pixel_value) - len(bits_to_embed)] + bits_to_embed
    #print("newpixval ", new_binary_pixel_value)
    #print("intnewpix (ref) ", int(new_binary_pixel_value, 2), "intpix", int_pixel_value)
    #print("chanel", channel_difference, " newdiff ", quantizationTable(abs(int(new_binary_pixel_value, 2) - int_pixel_value)))
    #if quantizationTable(abs(int(new_binary_pixel_value, 2) - int_pixel_value)) != channel_difference:
    #    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #    return int_reference_pixel_value

    global_binary_payload = global_binary_payload[channel_difference:]
    print("newpixval ", new_binary_pixel_value)
    return int(new_binary_pixel_value, 2)


def extractBits(channel_difference, int_pixel_value):
    binary_pixel_value = bin(int_pixel_value)[2:].zfill(8)

    extracted_bits = binary_pixel_value[len(binary_pixel_value) - channel_difference:]
    #print("binpixval ", binary_pixel_value, " channel ", channel_difference, " extracted ", extracted_bits)
    return extracted_bits


def main():
    global global_binary_secret, global_embed_counter, global_payload_size
    length_flag = 0
    secret_size = 0


    if global_encode_decode_flag == 'e':
        print("image capacity: ", capacity())
        if capacity() < global_payload_size:
            sys.exit("payload > capcity")
        if capacity() < 32:
            sys.exit("not space for size header")

        for image_y in range(0, global_image_height):
            for image_x in range(0, global_image_width, 2):
                if image_x + 1 == global_image_width:
                    break

                #print(image_x, image_y)
                tuple = global_rgb_data[image_y, image_x]

                red_reference_pixel, green_reference_pixel, blue_reference_pixel = tuple[0], tuple[1], tuple[2]

                tuple = global_rgb_data[image_y, image_x + 1]
                red_pixel, green_pixel, blue_pixel = tuple[0], tuple[1], tuple[2]

                red_pixel_difference = abs(red_pixel - red_reference_pixel)
                green_pixel_difference = abs(green_pixel - green_reference_pixel)
                blue_pixel_difference = abs(blue_pixel - blue_reference_pixel)
                if red_pixel_difference == 17:

                elif 33 <= red_pixel_difference <= 35:
                        new_red_pixel = embedBits(quantizationTable(red_pixel_difference), red_reference_pixel, red_pixel)

                new_green_pixel = embedBits(quantizationTable(green_pixel_difference), green_reference_pixel, green_pixel)
                new_blue_pixel = embedBits(quantizationTable(blue_pixel_difference), blue_reference_pixel, blue_pixel)

                global_rgb_data[image_y, image_x] = (new_red_pixel, new_green_pixel, new_blue_pixel)
                if len(global_binary_payload) == 0:
                    cover_image.save("stego_obj_" + sys.argv[2])
                    sys.exit("embed completed")


    elif global_encode_decode_flag == 'd':

        for image_y in range(0, global_image_height):
            for image_x in range(0, global_image_width, 2):
                if image_x + 1 == global_image_width:
                    break

                #print(image_x, image_y)
                tuple = global_rgb_data[image_y, image_x]

                red_reference_pixel, green_reference_pixel, blue_reference_pixel = tuple[0], tuple[1], tuple[2]

                tuple = global_rgb_data[image_y, image_x + 1]
                red_pixel, green_pixel, blue_pixel = tuple[0], tuple[1], tuple[2]

                red_pixel_difference = abs(red_pixel - red_reference_pixel)
                green_pixel_difference = abs(green_pixel - green_reference_pixel)
                blue_pixel_difference = abs(blue_pixel - blue_reference_pixel)
                #print("r ", quantizationTable(red_pixel_difference), " g ", quantizationTable(green_pixel_difference),
                #      " b ", quantizationTable(blue_pixel_difference))
                #print("ref pix r ", red_reference_pixel, " g ", green_reference_pixel, " b ", blue_reference_pixel)
                #print("pixel r ", red_pixel, " g ", green_pixel, " b ", blue_pixel)
                #print("pixeldifference r ", red_pixel_difference, " g ", green_pixel_difference, " b ",
                #      blue_pixel_difference)

                red_channel_bits = extractBits(quantizationTable(red_pixel_difference), red_reference_pixel)
                green_channel_bits = extractBits(quantizationTable(green_pixel_difference), green_reference_pixel)
                blue_channel_bits = extractBits(quantizationTable(blue_pixel_difference), blue_reference_pixel)

                # print("r ", red_channel_bits, " g ", green_channel_bits, " b ", blue_channel_bits)
                pixel_secret_bits = red_channel_bits + green_channel_bits + blue_channel_bits
                # print("secretbits ", pixel_secret_bits)
                #print("secret size", secret_size, "lengthflag", length_flag)
                #print("globalbinsec", global_binary_secret, "length", len(global_binary_secret))
                if length_flag == 0:
                    if len(global_binary_secret) >= 32:
                        bin_secret_size = global_binary_secret[:32]
                        secret_size = int(bin_secret_size, 2)
                        global_binary_secret = global_binary_secret[32:]
                        length_flag = 1

                global_binary_secret = global_binary_secret + pixel_secret_bits
                if length_flag == 1:
                    if len(global_binary_secret) >= secret_size:
                        global_binary_secret = global_binary_secret[:secret_size]
                        break

        print("secret ", global_binary_secret)
        s = int(global_binary_secret, 2)
        print(s.to_bytes((s.bit_length() + 7) // 8, 'big').decode())


if __name__ == "__main__":
    main()
