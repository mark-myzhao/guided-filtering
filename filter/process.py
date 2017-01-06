import filter.GuidedFilter as filter
import filter.FastGuidedFilter as fastFilter
import filter.CIPGuidedFilter as cipFilter
import filter.FastCIPGuidedFilter as fastCIPFilter
import filter.util as util

from PIL import Image
from math import floor


# Image Smoothing 评估算法的边缘保留特性
def image_smoothing(img_path, output_path, filter_radius=3, epsilon=0.2):
    test = filter.GuideFilter()
    test.read_img(img_path)
    test.set_guide(img_path)
    test.set_filter_radius(filter_radius)
    test.set_epsilon(epsilon * epsilon)
    test.run()
    res = test.get_res_img()
    if not (res is None):
        res.save(output_path)


# Image Detail Enhancement
def image_enhancement(img_path, output_path, filter_radius=3, epsilon=0.2, k=1):
    origin_img = Image.open(img_path)
    origin_pixels = list(origin_img.getdata())
    mood = ['r', 'g', 'b']
    res = []
    for i in range(3):
        test = cipFilter.CIPGuideFilter()
        test.read_img(img_path, mood[i])
        test.set_guide(img_path)
        test.set_filter_radius(filter_radius)  # means a 5 * 5 filter
        test.set_epsilon(epsilon * epsilon)
        test.run()
        res.append(test.get_res_img())
    merged_img = util.merge_image(res[0], res[1], res[2])
    pixels = list(merged_img.getdata())
    new_pixels = []
    for i in range(len(pixels)):
        new_pixel = []
        for j in range(3):
            tmp = floor(k * (origin_pixels[i][j] - pixels[i][j]) + origin_pixels[i][j])
            tmp = 0 if tmp < 0 else tmp
            tmp = 255 if tmp > 255 else tmp
            new_pixel.append(tmp)
        new_pixels.append((new_pixel[0], new_pixel[1], new_pixel[2]))
    new_img = Image.new('RGB', merged_img.size)
    new_img.putdata(new_pixels)
    new_img.save(output_path)


# 同样的输入和参数，使用快速引导滤波算法
def fast_image_smoothing(img_path, output_path, filter_radius=3, epsilon=0.2, s=4):
    test = fastFilter.FastGuideFilter()
    test.read_img(img_path)
    test.set_sample_ratio(s)
    test.set_guide(img_path)
    test.set_filter_radius(filter_radius)  # means a 5 * 5 filter
    test.set_epsilon(epsilon * epsilon)
    test.run()
    res = test.get_res_img()
    if not (res is None):
        res.save(output_path)


# 同样的输入和参数，使用快速引导滤波算法进行图像细节增强
def fast_image_enhancement(img_path, output_path, filter_radius=3, epsilon=0.2, k=1, s=2.0):
    origin_img = Image.open(img_path)
    origin_pixels = list(origin_img.getdata())
    mood = ['r', 'g', 'b']
    res = []
    for i in range(3):
        test = fastCIPFilter.FastCIPGuidedFilter()
        test.read_img(img_path, mood[i])
        test.set_sample_ratio(s)
        test.set_guide(img_path)
        test.set_filter_radius(filter_radius)  # means a 5 * 5 filter
        test.set_epsilon(epsilon * epsilon)
        test.run()
        res.append(test.get_res_img())
    merged_img = util.merge_image(res[0], res[1], res[2])
    merged_img.save('../output/img_enhancement/fast_monarch_res_rgb.bmp')
    pixels = list(merged_img.getdata())
    new_pixels = []
    for i in range(len(pixels)):
        new_pixel = []
        for j in range(3):
            tmp = floor(k * (origin_pixels[i][j] - pixels[i][j]) + origin_pixels[i][j])
            tmp = 0 if tmp < 0 else tmp
            tmp = 255 if tmp > 255 else tmp
            new_pixel.append(tmp)
        new_pixels.append((new_pixel[0], new_pixel[1], new_pixel[2]))
    new_img = Image.new('RGB', merged_img.size)
    new_img.putdata(new_pixels)
    new_img.save(output_path)
