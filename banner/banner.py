from collections import namedtuple
import os
import textwrap
import time
from rembg.bg import remove
import numpy as np
import io

from PIL import Image, ImageDraw, ImageFont, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import requests
#626x417
ASSET_DIR = 'assets'
DEFAULT_WIDTH = 626
DEFAULT_HEIGHT = 417
DEFAULT_CANVAS_SIZE = (DEFAULT_WIDTH, DEFAULT_HEIGHT)
DEFAULT_OUTPUT_FILE = 'out.png'
RESIZE_PERCENTAGE = 0.8
DEFAULT_TOP_MARGIN = int(((1 - 0.8) * DEFAULT_HEIGHT) / 2)
IMAGES = 'images'
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
WHITE_TRANSPARENT_OVERLAY = (255, 255, 255, 178)

TEXT_FONT_TYPE = os.path.join(ASSET_DIR, 'Roboto/Roboto-Light.ttf')
TITLE_FONT_TYPE = os.path.join(ASSET_DIR, 'Roboto/Roboto-Regular.ttf')
PRICE_FONT_TYPE = os.path.join(ASSET_DIR, 'Roboto/Roboto-Light.ttf')
BTN_FONT_TYPE = os.path.join(ASSET_DIR, 'Roboto/Roboto-Regular.ttf')

TEXT_PADDING_HOR = 15
X_LOGO_START = 15
Y_LOGO_START = 15
X_TITLE_START = 180
Y_TITLE_START = 10
X_TEXT_START = 15
Y_TEXT_START = 80
X_PRICE_START = 15
Y_PRICE_START = 270
X_DISCOUNT_START = 15
Y_DISCOUNT_START = 340
X_BTN_START = 447
Y_BTN_START = 340


# adjust CHARS_PER_LINE if you change TEXT_SIZE
TITLE_SIZE = 24
TEXT_SIZE = 18
PRICE_SIZE = 30
DISCOUNT_SIZE = 30
CHARS_PER_LINE = 30

Font = namedtuple('Font', 'ttf text color size offset')
Font_titulo = namedtuple('Font_titulo', 'ttf text color size offset')
Font_price = namedtuple('Font_price', 'ttf text color size offset')
Font_discount = namedtuple('Font_discount', 'ttf text color size offset')
Font_boton = namedtuple('Font_boton', 'ttf text color size offset')
ImageDetails = namedtuple('Image', 'left top size')


class Banner:
    def __init__(self, size=DEFAULT_CANVAS_SIZE,
                 bgcolor=WHITE, output_file=DEFAULT_OUTPUT_FILE):
        '''Creating a new canvas'''
        self.size = size
        self.width = size[0]
        self.height = size[1]
        self.bgcolor = bgcolor
        self.output_file = self._create_uniq_file_name(output_file)
        self.image = Image.new('RGBA', self.size, self.bgcolor)
        self.image_coords = []

    def _create_uniq_file_name(self, outfile):
        fname, ext = os.path.splitext(outfile)
        tstamp = str(time.time()).replace('.', '_')
        uniq_fname = '{}_{}{}'.format(fname, tstamp, ext)
        return os.path.join(IMAGES, uniq_fname)

    def _image_gt_canvas_size(self, img):
        return img.size[0] > self.image.size[0] or \
               img.size[1] > self.image.size[1]

    def add_image(self, image, resize=False, top=DEFAULT_TOP_MARGIN, left=0, right=False, remove_bg=False):
        '''Adds (pastes) image on canvas
           If right is given calculate left, else take left
           Returns added img size'''

        img = Image.open(image)

        if remove_bg:

            f = np.fromfile(image)
            result = remove(f)
            img = Image.open(io.BytesIO(result)).convert("RGBA")

        if resize or self._image_gt_canvas_size(img):
            size = self.height * RESIZE_PERCENTAGE
            img.thumbnail((size, size), Image.ANTIALIAS)

        if right:
            left = self.image.size[0] - img.size[0]

        offset = (left, top)

        self.image.paste(img.convert('RGBA'), offset, mask=img.convert('RGBA'))

        img_details = ImageDetails(left=left, top=top, size=img.size)
        self.image_coords.append(img_details)

    def add_logo(self, image, resize=False,
                  top=DEFAULT_TOP_MARGIN, left=0, right=False):
        '''Adds (pastes) image on canvas
           If right is given calculate left, else take left
           Returns added img size'''
        img = Image.open(image)

        size = self.height * RESIZE_PERCENTAGE
        img.thumbnail((150, 150), Image.ANTIALIAS)

        
        top = Y_LOGO_START
        left = X_LOGO_START

        offset = (left, top)
        self.image.paste(img.convert('RGBA'), offset, mask=img.convert('RGBA'))

        img_details = ImageDetails(left=left, top=top, size=img.size)
        self.image_coords.append(img_details)

    def add_text(self, font):
        '''Adds text on a given image object'''
        draw = ImageDraw.Draw(self.image)
        pillow_font = ImageFont.truetype(font.ttf, font.size)

        # from https://stackoverflow.com/a/7698300
        # if only 1 image use the extra space for text
        single_image = len(self.image_coords) == 1
        text_width = CHARS_PER_LINE * 1.4 if single_image else CHARS_PER_LINE

        lines = textwrap.wrap(font.text, width=text_width)

        if font.offset:
            x_text, y_text = font.offset
        else:
            # if no offset given put text alongside first image
            left_image_px = min(img.left + img.size[0]
                                for img in self.image_coords)

            x_text = left_image_px + TEXT_PADDING_HOR
            x_text = X_TEXT_START

            # if <= 2 lines center them more vertically
            y_text = Y_TEXT_START * 2 if len(lines) < 3 else Y_TEXT_START

        for line in lines:
            _, height = pillow_font.getsize(line)
            draw.text((x_text, y_text), line, font.color, font=pillow_font)
            y_text += height

    def add_titulo(self, font):

        '''Adds text on a given image object'''
        draw = ImageDraw.Draw(self.image)
        pillow_font = ImageFont.truetype(font.ttf, font.size)

        # from https://stackoverflow.com/a/7698300
        # if only 1 image use the extra space for text
        single_image = len(self.image_coords) == 1
        text_width = CHARS_PER_LINE * 1.4 if single_image else CHARS_PER_LINE

        lines = textwrap.wrap(font.text, width=text_width)

        if font.offset:
            x_text, y_text = font.offset
        else:
            # if no offset given put text alongside first image
            left_image_px = min(img.left + img.size[0]
                                for img in self.image_coords)

            x_text = X_TITLE_START

            # if <= 2 lines center them more vertically
            y_text = Y_TITLE_START * 1 if len(lines) < 3 else Y_TITLE_START

        for line in lines:
            _, height = pillow_font.getsize(line)
            draw.text((x_text, y_text), line, font.color, font=pillow_font)
            y_text += height+5

    def add_price(self, font):

        pad=15

        '''Adds text on a given image object'''
        draw = ImageDraw.Draw(self.image)
        pillow_font = ImageFont.truetype(font.ttf, font.size)
    
        size_width, size_height = draw.textsize(font.text, pillow_font)
        draw.rectangle((X_PRICE_START, Y_PRICE_START, size_width+X_PRICE_START+pad*2, Y_PRICE_START + 60), fill='#fbfb88')
        draw.text((X_PRICE_START+pad, Y_PRICE_START+pad), font.text, font.color, font=pillow_font)

    def add_discount(self, font):

        pad=15

        '''Adds text on a given image object'''
        draw = ImageDraw.Draw(self.image)
        pillow_font = ImageFont.truetype(font.ttf, font.size)
    
        size_width, size_height = draw.textsize(font.text, pillow_font)
        draw.rectangle((X_DISCOUNT_START, Y_DISCOUNT_START, size_width+X_DISCOUNT_START+pad*2, Y_DISCOUNT_START + 60), fill='#e72a2a')
        draw.text((X_DISCOUNT_START+pad, Y_DISCOUNT_START+pad), font.text, 'white', font=pillow_font)
     

    def add_boton(self, font):

        pad=15

        '''Adds text on a given image object'''
        draw = ImageDraw.Draw(self.image)
        pillow_font = ImageFont.truetype(font.ttf, font.size)
    
        size_width, size_height = draw.textsize(font.text, pillow_font)
    
        draw.rectangle((X_BTN_START, Y_BTN_START, X_BTN_START + 160, Y_BTN_START + 60), fill='#24b56a')
        draw.text((X_BTN_START+pad, Y_BTN_START+pad), font.text, 'white', font=pillow_font)

    def add_background(self, image, transparency=False, resize=False):
        img = Image.open(image).convert('RGBA')
        bg_img = img

        if transparency:
            overlay = Image.new('RGBA', img.size, WHITE_TRANSPARENT_OVERLAY)
            bg_img = Image.alpha_composite(img, overlay)

        if resize:
            bg_size = (self.width * RESIZE_PERCENTAGE, self.height)
            bg_img.thumbnail(bg_size, Image.ANTIALIAS)
            left = self.width - bg_img.size[0]
            self.image.paste(bg_img, (left, 0))
        else:
            self.image.paste(bg_img.resize(DEFAULT_CANVAS_SIZE,
                                           Image.ANTIALIAS), (0, 0))

    def save_image(self):
        self.image.save(self.output_file)


def _download_image(from_url, to_file, chunk_size=2000):
    r = requests.get(from_url, stream=True)

    with open(to_file, 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)


def get_image(image_url):
    basename = os.path.basename(image_url)
    local_image = os.path.join(IMAGES, basename)

    if not os.path.isfile(local_image):
        _download_image(image_url, local_image)

    return local_image


def generate_banner(img_banner):
    image1 = img_banner.image1
    image2 = get_image(img_banner.image2)
    text = img_banner.text
    titulo = img_banner.name
    price = img_banner.price
    discount = img_banner.discount
    background = get_image(img_banner.background)
    
    banner = Banner()

    if background!='':
        if img_banner.background_transparency:
            banner.add_background(background, True)
        else:
            banner.add_background(background, False)
    
    if img_banner.remove_background:

        banner.add_image(image2, resize=True, right=True, remove_bg=True)

    else:

        banner.add_image(image2, resize=True, right=True, remove_bg=False)

    banner.add_logo(image1)

    

    font_titulo = Font_titulo(ttf=TITLE_FONT_TYPE,
                text=titulo,
                color=BLACK,
                size=TITLE_SIZE,
                offset=None)

    banner.add_titulo(font_titulo)

    font = Font(ttf=TEXT_FONT_TYPE,
                text=text,
                color=BLACK,
                size=TEXT_SIZE,
                offset=None)

    font_price = Font_price(ttf=PRICE_FONT_TYPE,
                text=price,
                color=BLACK,
                size=PRICE_SIZE,
                offset=None)

    font_discount = Font_discount(ttf=PRICE_FONT_TYPE,
                text=discount,
                color=BLACK,
                size=DISCOUNT_SIZE,
                offset=None)

    font_boton = Font_boton(ttf=BTN_FONT_TYPE,
                text='VER MÁS',
                color=BLACK,
                size=DISCOUNT_SIZE,
                offset=None)

    banner.add_text(font)
    banner.add_price(font_price)
    banner.add_discount(font_discount)
    banner.add_boton(font_boton)

    banner.save_image()

    return banner.output_file
