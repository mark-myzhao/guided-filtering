import filter.GuidedFilter as filter
import filter.CIPGuidedFilter as cipFilter
import filter.util as util

from PIL import Image
from math import floor
from time import clock


# Image Smoothing
def image_smoothing():
    test = filter.GuideFilter()
    test.read_img('../input/img_smoothing/lena.bmp')
    test.set_guide('../input/img_smoothing/lena.bmp')
    test.set_filter_radius(8)  # means a 5 * 5 filter
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
        test = cipFilter.CIPGuidedFilter()
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


def fast_image_smoothing():
    img = Image.open('../input/img_enhancement/bird.bmp')
    pixels_rgb = list(img.getdata())
    nw = floor(img.width / 1.5)
    nh = floor(img.height / 1.5)
    new_pixel_r = util.sample(util.list_to_matrix(util.get_one_channel(pixels_rgb, 'R'), img.width, img.height), nw, nh)
    new_pixel_g = util.sample(util.list_to_matrix(util.get_one_channel(pixels_rgb, 'G'), img.width, img.height), nw, nh)
    new_pixel_b = util.sample(util.list_to_matrix(util.get_one_channel(pixels_rgb, 'B'), img.width, img.height), nw, nh)
    new_img_r = Image.new('L', (nw, nh))
    new_img_g = Image.new('L', (nw, nh))
    new_img_b = Image.new('L', (nw, nh))
    new_img_r.putdata(util.matrix_to_list(new_pixel_r))
    new_img_g.putdata(util.matrix_to_list(new_pixel_g))
    new_img_b.putdata(util.matrix_to_list(new_pixel_b))
    new_img_r.save('../output/test_r.bmp')
    new_img_g.save('../output/test_g.bmp')
    new_img_b.save('../output/test_b.bmp')
    new_img = util.merge_image(new_img_r, new_img_g, new_img_b)
    new_img.save('../output/test_rgb.bmp')

fast_image_smoothing()

# # 测试步骤
# start_total = clock()
# process_list = [
#                 # ('../input/img_enhancement/monarch.bmp', '../output/img_enhancement/monarch_res.bmp'),
#                 # ('../input/img_enhancement/bird.bmp', '../output/img_enhancement/bird_res.bmp'),
#                 # ('../input/img_enhancement/starynight.bmp', '../output/img_enhancement/starynight_res.bmp'),
#                 # ('../input/img_enhancement/tomato.bmp', '../output/img_enhancement/tomato_res.bmp'),
#                 # ('../input/img_enhancement/tulips.bmp', '../output/img_enhancement/tulips_res.bmp')
#                 ]
# i = 0
# for path in process_list:
#     i += 1
#     start = clock()
#     image_enhancement(path[0], path[1], 16, 0.2, 1)
#     finish = clock()
#     print('image ' + str(i) + ' processing time: ' + str(finish - start) + 's')
# finish_total = clock()
# print('total processing time: ' + str(finish_total - start_total) + 's')
