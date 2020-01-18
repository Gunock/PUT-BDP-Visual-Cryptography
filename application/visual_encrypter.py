from math import floor
from random import randint

import numpy as np
from cv2 import cv2

share_1_global: np.ndarray
share_2_global: np.ndarray
denoise: bool = False
fix_proportion: bool = False
offset: int = 0


def _denoise_decrypted_image(img: np.ndarray):
    i: int = 0
    shape_0: int = img.shape[0]
    shape_1: int = img.shape[1]
    pixel_sum: int
    half_pixel_sum_value: int = 255 * int(shape_1 / 2)

    while i < shape_0:
        if img[i].sum() == half_pixel_sum_value:
            img[i, 0:shape_1] = 0
        elif not np.all(img[i]):
            j: int = 0
            while j < shape_1:
                if img[i, j] != img[i, j + 1]:
                    img[i, j:j + 2] = 0
                j += 2
        i += 1


def _fix_decrypted_image_proportion(src: np.ndarray) -> np.ndarray:
    return cv2.resize(src, (int(src.shape[1] / 2), src.shape[0]))


def decrypt(share_1: np.ndarray, share_2: np.ndarray, denoise: bool = True, fix_proportions: bool = True):
    result: np.ndarray = cv2.add(share_1, share_2)
    if denoise:
        _denoise_decrypted_image(result)
    if fix_proportions:
        result = _fix_decrypted_image_proportion(result)
    return result


def _fill_shares(src: np.ndarray, share_1: np.ndarray, share_2: np.ndarray):
    i: int = 0
    while i < src.shape[0]:
        j: int = 0
        while j < src.shape[1]:
            combination: bool = randint(0, 1)
            if src[i, j] > 127:
                share_1[i, j * 2: j * 2 + 2] = (255, 0) if combination else (0, 255)
                share_2[i, j * 2: j * 2 + 2] = (255, 0) if combination else (0, 255)
            else:
                share_1[i, j * 2: j * 2 + 2] = (0, 255) if combination else (255, 0)
                share_2[i, j * 2: j * 2 + 2] = (255, 0) if combination else (0, 255)
            j += 1
        i += 1


def _overlap_shares(share_1: np.ndarray, share_2: np.ndarray, value: int):
    background: np.ndarray = np.full(shape=[share_1.shape[0] * 2, share_1.shape[1]], dtype=np.uint8,
                                     fill_value=255)
    background[share_1.shape[0] - value:share_1.shape[0] * 2 - value, 0:share_2.shape[1]] = share_2
    background[0:share_1.shape[0], 0:share_1.shape[1]] = share_1

    background_part = background[share_1.shape[0] - value:share_1.shape[0] * 2 - value, 0:share_2.shape[1]]
    added_shares = cv2.add(background_part, share_2)

    background[share_1.shape[0] - value:share_1.shape[0] * 2 - value, 0:share_2.shape[1]] = added_shares
    return background


def _show_overlapped_shares():
    global share_1_global, share_2_global, denoise, fix_proportion, offset
    overlapped_shares: np.ndarray = _overlap_shares(share_1_global, share_2_global, offset)
    if denoise:
        _denoise_decrypted_image(overlapped_shares)
    if fix_proportion:
        overlapped_shares = _fix_decrypted_image_proportion(overlapped_shares)
    overlapped_shares = cv2.bitwise_not(overlapped_shares)

    border_size: int = 200 - floor(overlapped_shares.shape[1] / 2)
    if border_size > 0:
        overlapped_shares = cv2.copyMakeBorder(overlapped_shares, 0, 0, border_size, border_size, cv2.BORDER_CONSTANT)

    cv2.imshow("application", overlapped_shares)


def _callback_1(value: int):
    global offset
    offset = value
    _show_overlapped_shares()


def _callback_2(value: bool):
    global denoise
    denoise = value
    _show_overlapped_shares()


def _callback_3(value: bool):
    global fix_proportion
    fix_proportion = value
    _show_overlapped_shares()


def _create_share_overlap_window(share_1, share_2):
    global share_1_global, share_2_global, denoise, fix_proportion, offset

    share_1_global = share_1
    share_2_global = share_2

    cv2.namedWindow("application")
    cv2.createTrackbar("Overlap", "application", 0, share_1.shape[0], _callback_1)
    cv2.createTrackbar("Denoise", "application", 0, 1, _callback_2)
    cv2.createTrackbar("Fix proportions", "application", 0, 1, _callback_3)
    _show_overlapped_shares()

    cv2.waitKey()
    cv2.destroyAllWindows()
    denoise = False
    fix_proportion = False
    offset = 0


def _create_shares(src):
    share_1: np.ndarray = np.zeros(shape=[src.shape[0], src.shape[1] * 2], dtype=np.uint8)
    share_2: np.ndarray = np.zeros(shape=[src.shape[0], src.shape[1] * 2], dtype=np.uint8)
    _fill_shares(src, share_1, share_2)
    return share_1, share_2


def visualize_encryption(filename: str, save_shares: bool):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    share_1, share_2 = _create_shares(img)
    _create_share_overlap_window(share_1, share_2)

    if save_shares:
        filename_split: list = filename.split('.')
        share_1_filename: str = filename_split[0] + '_share_1.' + filename_split[1]
        share_2_filename: str = filename_split[0] + '_share_2.' + filename_split[1]
        cv2.imwrite(share_1_filename, share_1)
        cv2.imwrite(share_2_filename, share_2)
