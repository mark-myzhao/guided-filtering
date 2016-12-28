import filter.GuidedFilter as filter
import filter.CIPGuideFilter as cipFilter
import filter.util as util

from PIL import Image
from math import floor


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
def image_enhancement():
    test = cipFilter.CIPGuideFilter()
    mood = ['r', 'g', 'b']
    for i in range(3):
        test.read_img('../input/img_enhancement/bird.bmp', mood[i])
        test.set_guide('../input/img_enhancement/bird.bmp')
        test.set_filter_radius(3)  # means a 5 * 5 filter
        test.set_epsilon(0.2 * 0.2)
        test.run()
        res_img = test.get_res_img()
        res_img.save('../output/test_' + mood[i] + '.png')

# image_enhancement()
# res = [Image.open('../output/test_b.png'),
#        Image.open('../output/test_g.png'),
#        Image.open('../output/test_b.png')]
# output = util.merge_image(res[0], res[1], res[2])
# output.save('../output/test.png')
origin_img = Image.open('../input/img_enhancement/bird.bmp')
img = Image.open('../output/test.png')
origin_pixels = list(origin_img.getdata())
pixels = list(img.getdata())
new_pixels = []
for i in range(len(pixels)):
    new_pixel = []
    for j in range(3):
        tmp = floor(0.5 * (origin_pixels[i][j] - pixels[i][j]) + origin_pixels[i][j])
        tmp = 0 if tmp < 0 else tmp
        tmp = 255 if tmp > 255 else tmp
        new_pixel.append(tmp)
    new_pixels.append((new_pixel[0], new_pixel[1], new_pixel[2]))
new_img = Image.new('RGB', img.size)
new_img.putdata(new_pixels)
new_img.save('../output/test_en.png')
