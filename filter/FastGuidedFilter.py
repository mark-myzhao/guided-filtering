from PIL import Image
from math import floor

import filter.util as util


# 仅用灰度图像作为Guide进行引导滤波
class FastGuideFilter(object):
    def __init__(self):
        self.origin_p = None  # origin img
        self.origin_guide = None  # origin guide matrix
        self.p = None  # sampled source image matrix, padded after set_filter_radius()
        self.guide = None  # sampled guide image matrix, padded after set_filter_radius()
        self.q = None  # target image matrix
        self.__epsilon = None  # a small number epsilon, set by user
        self.__p_buff = None  # box filter method buffer
        self.__guide_buff = None  # box filter method buffer
        self.__pg_buff = None  # box filter method buffer
        self.__p2_buff = None  # box filter method buffer
        self.__a_buff = None  # box filter buffer of parameter a
        self.__b_buff = None  # box filter buffer of parameter b
        self.__origin_img_size = None  # source size, (width, height)
        self.__img_size = None  # sampled image size
        self.__padding_img_size = None  # size of padding image, (width, height)
        self.__filter_radius = None  # filter radius
        self.__s = None  # sample ratio

    # --- init methods, parameters should be set by user ---
    def read_img(self, img_path):
        img = Image.open(img_path)
        pixels = list(img.getdata())
        # normalize operation [0-255] -> [0-1]
        for i in range(len(pixels)):
            pixels[i] /= 255.0
        self.p = util.list_to_matrix(pixels, img.width, img.height)
        self.origin_p = img
        self.__img_size = img.size
        self.__origin_img_size = img.size

    # 设置采样率，需要在set_guide和set_filter_radius之前调用
    def set_sample_ratio(self, rs):
        self.__s = rs
        nw, nh = floor(self.__img_size[0] / rs), floor(self.__img_size[1] / rs)
        self.__img_size = nw, nh
        self.p = util.sample(self.p, nw, nh)

    def set_guide(self, guide_path):
        img = Image.open(guide_path)
        # guide size should be equal to source size
        if img.size == self.__origin_img_size:
            pixels = list(img.getdata())
            # normalize operation [0-255] -> [0-1]
            for i in range(len(pixels)):
                pixels[i] /= 255.0
            self.origin_guide = util.list_to_matrix(pixels, img.width, img.height)
            self.guide = util.sample(self.origin_guide, self.__img_size[0], self.__img_size[1])
        else:
            # error happens
            print('> Error: guide\'s size should be equal to source\'s size')
            return

    # set the radius of guided filter while padding source and guided images
    def set_filter_radius(self, r):
        self.__filter_radius = floor(r / self.__s)
        self.__padding_img_size = self.__img_size[0] + 2 * self.__filter_radius, self.__img_size[1] + 2 * self.__filter_radius
        self.p = util.padding(self.p, self.__filter_radius)
        self.guide = util.padding(self.guide, self.__filter_radius)

    def set_epsilon(self, e):
        self.__epsilon = e

    # --- kernel algorithm ---
    def run(self):
        mean_a, mean_b = [], []
        if self.p is None or self.guide is None or self.__epsilon is None:
            return False
        self.__calculate_box_buff()
        self.q = []
        r = self.__filter_radius
        for i in range(r, r + self.__img_size[1]):
            mean_a_row, mean_b_row = [], []
            for j in range(r, r + self.__img_size[0]):
                aver_a, aver_b = self.__calculate_aver_ab_at(i, j)
                mean_a_row.append(aver_a)
                mean_b_row.append(aver_b)
            mean_a.append(mean_a_row)
            mean_b.append(mean_b_row)
        # 上采样
        mean_a = util.sample(mean_a, self.__origin_img_size[0], self.__origin_img_size[1])
        mean_b = util.sample(mean_b, self.__origin_img_size[0], self.__origin_img_size[1])
        for i in range(self.__origin_img_size[1]):
            q_row = []
            for j in range(self.__origin_img_size[0]):
                result = mean_a[i][j] * self.origin_guide[i][j] + mean_b[i][j]
                q_row.append(result)
            self.q.append(q_row)
        return True

    # --- get Methods ---
    def get_size(self):
        return self.__img_size

    def get_filter_size(self):
        return self.__filter_radius * 2 + 1

    def get_res_img(self):
        img = self.origin_p.copy()
        res_pixels = util.matrix_to_list(self.q)
        # normalize [0-1] -> [0-255]
        for i in range(len(res_pixels)):
            res_pixels[i] = floor(res_pixels[i] * 255.0)
        if self.q is None:
            print('> Error: Algorithm has not finished')
        else:
            img.putdata(res_pixels)
        return img

    # --- internal methods, used to implement the kernel algorithm ---
    def __calculate_box_buff(self):
        self.__p_buff = util.calculate_box(self.p)
        self.__guide_buff = util.calculate_box(self.guide)
        self.__pg_buff = util.calculate_box(util.array_multiply(self.p, self.guide))
        self.__p2_buff = util.calculate_box(util.array_multiply(self.p, self.p))
        self.__calculate_ab_buff()

    def __calculate_ab_buff(self):
        param_a, param_b = [], []
        r = self.__filter_radius
        w, h = self.__img_size[0], self.__img_size[1]
        # a and b in padding positions are simply set to 0
        for i in range(r):
            param_a.append([0 for k in range(self.__padding_img_size[0])])
            param_b.append([0 for k in range(self.__padding_img_size[0])])
        for i in range(r, r + h):
            tmp_a_row, tmp_b_row = [0.0 for k in range(r)], [0.0 for k in range(r)]
            # calculate a and b here
            for j in range(r, r + w):
                tmp_ab = self.__calculate_ab_at(i, j)
                tmp_a_row.append(tmp_ab[0])  # get a
                tmp_b_row.append(tmp_ab[1])  # get b
            tmp_a_row += [0.0 for k in range(r)]
            tmp_b_row += [0.0 for k in range(r)]
            param_a.append(tmp_a_row)
            param_b.append(tmp_b_row)
        for i in range(r + h, self.__padding_img_size[1]):
            param_a.append([0 for k in range(self.__padding_img_size[0])])
            param_b.append([0 for k in range(self.__padding_img_size[0])])
        self.__a_buff = util.calculate_box(param_a)
        self.__b_buff = util.calculate_box(param_b)

    # calculate a at position(x, y)
    # return result
    def __calculate_ab_at(self, x, y):
        r = self.__filter_radius
        w = (2 * r + 1) ** 2
        c = [  # positions of 4 corners
            [(x - r, y - r), (x - r, y + r)],
            [(x + r, y - r), (x + r, y + r)]
        ]
        sum_ip = util.calculate_sum(self.__pg_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        sum_i = util.calculate_sum(self.__guide_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        sum_p = util.calculate_sum(self.__p_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        sum_p2 = util.calculate_sum(self.__p2_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        aver_i = sum_i / float(w)
        aver_p = sum_p / float(w)
        sigma2 = sum_p2 / float(w) - (sum_p / float(w)) ** 2
        # print(sigma2)
        a_res = (sum_ip / float(w) - aver_i * aver_p) / float(sigma2 + self.__epsilon)
        b_res = aver_p - a_res * aver_i
        return a_res, b_res

    def __calculate_aver_ab_at(self, x, y):
        r = self.__filter_radius
        c = [
            [(x - r, y - r), (x - r, y + r)],
            [(x + r, y - r), (x + r, y + r)]
        ]
        sum_a = util.calculate_sum(self.__a_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        sum_b = util.calculate_sum(self.__b_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        w = self.get_filter_size() ** 2
        return sum_a / float(w), sum_b / float(w)
