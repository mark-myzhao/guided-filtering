import filter.GuidedFilter as filter
import filter.FastGuidedFilter as fastFilter
import filter.CIPGuidedFilter as cipFilter
import filter.FastCIPGuidedFilter as fastCIPFilter
import filter.util as util

from PIL import Image
from math import floor
from time import clock


# Image Smoothing
def image_smoothing():
    test = filter.GuideFilter()
    test.read_img('../input/img_smoothing/lena.bmp')
    test.set_guide('../input/img_smoothing/lena.bmp')
    test.set_filter_radius(4)  # means a 5 * 5 filter
    test.set_epsilon(0.2 * 0.2)
    test.run()
    res = test.get_res_img()
    if not (res is None):
        # res.show()
        res.save('../output/img_smoothing/lena_8.bmp')


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
    # res[0].save('../output/img_enhancement/monarch_res_r.bmp')
    # res[1].save('../output/img_enhancement/monarch_res_g.bmp')
    # res[2].save('../output/img_enhancement/monarch_res_b.bmp')
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


def fast_image_smoothing():
    test = fastFilter.FastGuideFilter()
    test.read_img('../input/img_smoothing/lena.bmp')
    test.set_sample_ratio(4)
    test.set_guide('../input/img_smoothing/lena.bmp')
    test.set_filter_radius(4)  # means a 5 * 5 filter
    test.set_epsilon(0.2 * 0.2)
    test.run()
    res = test.get_res_img()
    if not (res is None):
        # res.show()
        res.save('../output/img_smoothing/fast_lena_8.bmp')


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
    # debug
    # res[0].save('../output/img_enhancement/fast_monarch_res_r.bmp')
    # res[1].save('../output/img_enhancement/fast_monarch_res_g.bmp')
    # res[2].save('../output/img_enhancement/fast_monarch_res_b.bmp')
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


# s = clock()
# image_smoothing()
# s1 = clock()
# fast_image_smoothing()
# s2 = clock()

# print(s1 - s)
# print(s2 - s1)

# 测试步骤
print('--  Guided Filter Enhancement  --')
start_total = clock()
process_list = [
                ('../input/img_enhancement/monarch.bmp', '../output/img_enhancement/monarch_res.bmp'),
                ('../input/img_enhancement/bird.bmp', '../output/img_enhancement/bird_res.bmp'),
                ('../input/img_enhancement/starynight.bmp', '../output/img_enhancement/starynight_res.bmp'),
                ('../input/img_enhancement/tomato.bmp', '../output/img_enhancement/tomato_res.bmp'),
                ('../input/img_enhancement/tulips.bmp', '../output/img_enhancement/tulips_res.bmp')
                ]
i = 0
for path in process_list:
    i += 1
    start = clock()
    image_enhancement(path[0], path[1], 9, 0.2, 1)
    finish = clock()
    print('image ' + str(i) + ' processing time: ' + str(finish - start) + 's')
finish_total = clock()
print('total processing time: ' + str(finish_total - start_total) + 's')

# 测试步骤 快速引导滤波
print('')
print('--  Fast Guided Filter Enhancement  --')
start_total = clock()
process_list = [
                ('../input/img_enhancement/monarch.bmp', '../output/img_enhancement/fast_monarch_res.bmp'),
                ('../input/img_enhancement/bird.bmp', '../output/img_enhancement/fast_bird_res.bmp'),
                ('../input/img_enhancement/starynight.bmp', '../output/img_enhancement/fast_starynight_res.bmp'),
                ('../input/img_enhancement/tomato.bmp', '../output/img_enhancement/fast_tomato_res.bmp'),
                ('../input/img_enhancement/tulips.bmp', '../output/img_enhancement/fast_tulips_res.bmp')
                ]
i = 0
for path in process_list:
    i += 1
    start = clock()
    fast_image_enhancement(path[0], path[1], 9, 0.2, 1, 4.0)
    finish = clock()
    print('image ' + str(i) + ' processing time: ' + str(finish - start) + 's')
finish_total = clock()
print('total processing time: ' + str(finish_total - start_total) + 's')
