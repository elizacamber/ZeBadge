import time
import zlib

import board
import circuitpython_base64 as base64
import displayio

import zeos
from message import Message


class MessageKey:
    SHOW_GROUP = "SHOW_GROUP"
    SHOW_BITMAP = "SHOW_BITMAP"
    SHOW_FILE = "SHOW_FILE"
    SHOW_TERMINAL = "SHOW_TERMINAL"
    REFRESH = "REFRESH"


def init(os):
    os.subscribe(MessageKey.SHOW_GROUP, _show_group)
    os.subscribe(MessageKey.SHOW_BITMAP, _show_bitmap_handler)
    os.subscribe(MessageKey.SHOW_FILE, _show_file_handler)
    os.subscribe(MessageKey.SHOW_TERMINAL, _show_terminal_handler)
    os.subscribe(MessageKey.REFRESH, _refresh_handler)


def _refresh_display_save():
    time.sleep(board.DISPLAY.time_to_refresh + 0.3)

    try:
        board.DISPLAY.refresh()
    except:
        print("x")


def _refresh_handler(os, message):
    _refresh_display_save()


def _show_bitmap_handler(os, message):
    bitmap, palette = message.value
    del message

    _show_bitmap(bitmap, palette)


def _show_bitmap(bitmap, palette):
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

    group = displayio.Group()
    group.append(tile_grid)
    board.DISPLAY.root_group = group
    _refresh_display_save()


def _show_group(_, message):
    group = message.value
    board.DISPLAY.root_group = group
    _refresh_display_save()


def _show_file_handler(os, message):
    filename = message.value
    if not filename.endswith('.b64'):
        filename += '.b64'

    with open(filename, "rb") as file:
        payload = file.read()
        bitmap, palette = decode_serialized_bitmap(payload)
        del payload

        _show_bitmap(bitmap, palette)

        os.messages.append(Message(zeos.MessageKey.INFO, f"File '{filename}' shown. "))


def _show_terminal_handler(os, message):
    board.DISPLAY.root_group = displayio.CIRCUITPYTHON_TERMINAL
    _refresh_display_save()


def draw_intro():
    # splash = displayio.Group()
    #
    # splash_picture = displayio.OnDiskBitmap('/splash.bmp')
    # splash_tiles = displayio.TileGrid(splash_picture, pixel_shader=splash_picture.pixel_shader)
    # splash.append(splash_tiles)
    # display.root_group = splash

    _refresh_display_save()


def decode_serialized_bitmap(payload, width=296, height=128):
    compressed_bytes = base64.b64decode(payload)
    binarized_bytes = zlib.decompress(compressed_bytes)

    bitmap = displayio.Bitmap(width, height, 2)

    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = 0xFFFFFF

    for y in range(height):
        print("B", end="")
        for x in range(width):
            # Pretend you understand this part
            byte_index = (y * (width // 8)) + (x // 8)
            bit_index = 7 - (x % 8)
            pixel_value = (binarized_bytes[byte_index] >> bit_index) & 1
            bitmap[x, y] = pixel_value

    return bitmap, palette
