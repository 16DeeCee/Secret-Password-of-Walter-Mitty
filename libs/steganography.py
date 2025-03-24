# import numpy as np
from libs.logging import Logging
from PIL import Image
from typing import Any
# import os
import uuid
import base64


PIXEL_PATTERN = 5
DELIMITER = b"====="
log = Logging.getLogger()


class Steganography:
    def __init__(self, image_path: str, encrypted_data: bytes = None):
        self.image_path = image_path
        self.encrypted_data =  encrypted_data


    def encode_bytes_in_image(self) -> str:
        enc_data_binary = self.to_binary(self.encrypted_data + DELIMITER)
        enc_data_binary_size = len(enc_data_binary)

        image = Image.open(self.image_path)
        image_pixels = list(image.getdata())
        max_available_pixels = len(image_pixels) * 3 // PIXEL_PATTERN

        if enc_data_binary_size > max_available_pixels:
            raise ValueError("Image is too small. Please choose a bigger image.")

        log.debug("MAX AVAILABLE PIXELS: - %s SECRET DATA LENGTH: %s - ENCRYPTED DATA SIZE: %d" % 
            (max_available_pixels, enc_data_binary_size, enc_data_binary_size // 8)
        )

        enc_data_binary_size = self.to_binary(enc_data_binary_size // 8)

        log.debug("DATA SIZE IN BINARY: %s" % enc_data_binary_size)

        for index in range(len(enc_data_binary_size)):
            r, g, b = image_pixels[index]

            g = self.to_binary(g)
            g = int(g[:-1] + enc_data_binary_size[index], 2)

            image_pixels[index] = (r, g, b)


        log.info("ENCODING STARTED - IMAGE: %s" % self.image_path)
        for index, bit in enumerate(enc_data_binary):
            pixel_index = index * PIXEL_PATTERN
            r, g, b = image_pixels[pixel_index]

            b = self.to_binary(b)
            b = int(b[:-1] + bit, 2)

            image_pixels[pixel_index] = (r, g, b)
        
        image.putdata(image_pixels)

        log.info("ENCODING FINISHED.")

        image_path = f"images/{str(uuid.uuid4())}.png"
        image.save(image_path)

        return image_path
    
    
    def decode_bytes_in_image(self) -> bytes:
        image = Image.open(self.image_path)
        image_pixels = image.getdata()

        encrypted_data_size = ""
        encrypted_data = ""

        for index in range(8):
            pixel_g = self.to_binary(image_pixels[index][1])
            encrypted_data_size += pixel_g[-1]
        
        log.debug("DATA SIZE: %d" % int(encrypted_data_size, 2))

        encrypted_image_size = int(encrypted_data_size, 2) * 8 * 5

        log.info("DECODING STARTED - IMAGE: %s" % self.image_path)
        for index in range(0, encrypted_image_size, PIXEL_PATTERN):
            pixel_b = self.to_binary(image_pixels[index][2])
            encrypted_data += pixel_b[-1]

        log.info("BINARY TO BYTES CONVERSION STARTED.")
        data_bytes = bytes(int(encrypted_data[i:i + 8], 2) for i in range(0, len(encrypted_data), 8))

        log.info("HIDDEN DATA EXTRACTION COMPLETE.")

        return data_bytes.split(b"=====")[0]

    
    @staticmethod
    def to_binary(data: Any) -> str:
        '''Convert data bytes or int to binary string.'''
        if isinstance(data, bytes):
            return "".join([format(b, "08b") for b in data])
        
        if isinstance(data, int):
            return format(data, "08b")
        
        raise TypeError("Type is not supported")
    