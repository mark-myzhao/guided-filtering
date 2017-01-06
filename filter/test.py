from filter.process import *
from time import clock

# configuration
# 输入图片路径，输出图片路径，输入图片文件名，输入图片文件格式
root_dir = ('../input/', '../output/')
smoothing_dir = 'img_smoothing/'
enhancement_dir = 'img_enhancement/'
fast_smoothing_dir = 'fast_img_smoothing/'
fast_enhancement_dir = 'fast_img_enhancement/'
smoothing_input_image_list = [
    # 'baboon.bmp'，
    # 'beauty_with_freckle.bmp',
    # 'boy.bmp',
    'cat.bmp',
    'lena.bmp'
]
enhancement_input_image_list = [
    'monarch.bmp',
    'bird.bmp',
    'starynight.bmp',
    'tomato.bmp',
    'tulips.bmp'
]
# -- 配置参数在此处进行调整 --
# f: 滤波器窗口大小
# e: 标准差
# k: 图像增强系数
# s: 采样率
smoothing_config = (8, 0.4)  # (f, e)
enhancement_config = (9, 0.2, 1)  # (f, e, k)
fast_smoothing_config = (9, 0.2, 4.0)  # (f, e, s)
fast_enhancement_config = (9, 0.2, 1, 4.0)  # (f, e, k, s)

# 测试引导滤波 **边缘保留部分**
test_name = 's_'
print('--  Guided Filter Smoothing  --')
start_total = clock()
i = 0
for img_name in smoothing_input_image_list:
    path = (root_dir[0] + smoothing_dir + img_name,
            root_dir[1] + smoothing_dir + test_name + img_name)
    i += 1
    start = clock()
    image_smoothing(*path, *smoothing_config)
    finish = clock()
    print('image ' + str(i) + ' processing time: ' + str(finish - start) + 's')
finish_total = clock()
print('total processing time: ' + str(finish_total - start_total) + 's')
print('')

# 测试引导滤波 **图像增强部分**
# test_name = 'e_'
# print('--  Guided Filter Enhancement  --')
# start_total = clock()
# i = 0
# for img_name in enhancement_input_image_list:
#     path = (root_dir[0] + enhancement_dir + img_name,
#             root_dir[1] + enhancement_dir + test_name + img_name)
#     i += 1
#     start = clock()
#     image_enhancement(*path, *enhancement_config)
#     finish = clock()
#     print('image ' + str(i) + ' processing time: ' + str(finish - start) + 's')
# finish_total = clock()
# print('total processing time: ' + str(finish_total - start_total) + 's')
# print('')

# # 测试快速引导滤波 **边缘保留部分**
# test_name = 'fs_'
# print('-- Fast Guided Filter Smoothing  --')
# start_total = clock()
# i = 0
# for img_name in smoothing_input_image_list:
#     path = (root_dir[0] + smoothing_dir + img_name,
#             root_dir[1] + fast_smoothing_dir + test_name + img_name)
#     i += 1
#     start = clock()
#     fast_image_smoothing(*path, *fast_smoothing_config)
#     finish = clock()
#     print('image ' + str(i) + ' processing time: ' + str(finish - start) + 's')
# finish_total = clock()
# print('total processing time: ' + str(finish_total - start_total) + 's')
# print('')

# 测试快速引导滤波 **图像增强部分**
# test_name = 'fe_'
# print('--  Fast Guided Filter Enhancement  --')
# start_total = clock()
# i = 0
# for img_name in enhancement_input_image_list:
#     path = (root_dir[0] + enhancement_dir + img_name,
#             root_dir[1] + fast_enhancement_dir + test_name + img_name)
#     i += 1
#     start = clock()
#     fast_image_enhancement(*path, *fast_enhancement_config)
#     finish = clock()
#     print('image ' + str(i) + ' processing time: ' + str(finish - start) + 's')
# finish_total = clock()
# print('total processing time: ' + str(finish_total - start_total) + 's')
# print('')
