from PIL import Image
from math import floor

import numpy as np

import filter.util as util


# 使用彩色图像作为Guide进行引导滤波
# 适用于RGB任何通道都无显著边界的情况
class CIPGuideFilter(object):
    def __init__(self):
        # -- constant value --
        self.__GREY_LEVEL = 256.0
        # -- init value
        self.origin_p = None  # origin img
        self.p = None  # the matrix of **one channel** of source image, padded after set_filter_radius()
        self.guide_v = [None, None, None]  # guide image matrix (3-D vector), padded after set_filter_radius()
        self.q = None  # target matrix
        self.__epsilon = None  # a small number epsilon, set by user
        self.__p_buff = None  # box filter method buffer
        self.__guide_v_buff = [None, None, None]  # guide box buffer, divided into three part
        self.__guide2_v_buff = [None, None, None]  # guide ** 2 box buffer, used to calculate cov
        self.__guide_mix_v_buff = [None, None, None]  # g0g1, g0g2, g1g2 box buffer, used to calculate cov
        self.__pg_v_buff = [None, None, None]  # box filter method buffer, array of 3-D vector
        self.__a_v_buff = [None, None, None]  # box filter buffer of parameter a, array of 3-D vector
        self.__p2_buff = None  # box filter method buffer
        self.__b_buff = None  # box filter buffer of parameter b
        self.__img_size = None  # source size, (width, height)
        self.__padding_img_size = None  # size of padding image, (width, height)
        self.__filter_radius = None  # filter radius

    # --- init methods, parameters should be set by user ---
    # for grey image input
    def read_img(self, img_path, channel='l'):
        img = Image.open(img_path)
        pixels = list(img.getdata())
        new_pixels = []
        if channel == 'l':
            # normalize operation [0-255] -> [0-1]
            for pixel in pixels:
                new_pixels.append(pixel / (self.__GREY_LEVEL - 1))
        elif channel == 'r':
            for pixel in pixels:
                # 提取R通道并归一化
                new_pixels.append(pixel[0] / (self.__GREY_LEVEL - 1))
        elif channel == 'g':
            for pixel in pixels:
                # 提取G通道并归一化
                new_pixels.append(pixel[1] / (self.__GREY_LEVEL - 1))
        elif channel == 'b':
            for pixel in pixels:
                # 提取B通道并归一化
                new_pixels.append(pixel[2] / (self.__GREY_LEVEL - 1))
        else:
            print('> Error: channel is illegal')
        self.p = util.list_to_matrix(new_pixels, img.width, img.height)
        self.origin_p = img
        self.__img_size = img.size

    # notice that here guide is a color image
    def set_guide(self, guide_path):
        img = Image.open(guide_path)
        # guide size should be equal to source size
        if img.size == self.__img_size:
            pixels = list(img.getdata())
            new_pixels = [[], [], []]
            # normalize operation [0-255] -> [0-1]
            for pixel in pixels:
                for k in range(3):  # 分解成三个分量
                    new_pixels[k].append(pixel[k] / (self.__GREY_LEVEL - 1))
            for i in range(3):
                self.guide_v[i] = util.list_to_matrix(new_pixels[i], img.width, img.height)
        else:
            # error happens
            print('> Error: guide\'s size should be equal to source\'s size')
            return

    # set the radius of guided filter while padding source and guided images
    def set_filter_radius(self, r):
        self.__filter_radius = r
        self.__padding_img_size = self.__img_size[0] + 2 * r, self.__img_size[1] + 2 * r
        self.p = util.padding(self.p, r)
        for i in range(3):
            self.guide_v[i] = util.padding(self.guide_v[i], r)

    def set_epsilon(self, e):
        self.__epsilon = e

    # --- kernel algorithm ---
    def run(self):
        if self.p is None or self.guide_v is None or self.__epsilon is None:
            return False
        self.__calculate_box_buff()
        self.q = []
        r = self.__filter_radius
        for i in range(r, r + self.__img_size[1]):
            q_row = []
            for j in range(r, r + self.__img_size[0]):
                aver_a, aver_b = self.__calculate_aver_ab_at(i, j)
                i_tmp_v = np.array([[self.guide_v[0][i][j], self.guide_v[1][i][j], self.guide_v[2][i][j]]])
                tmp_a_v = np.array([aver_a])
                result = i_tmp_v.dot(tmp_a_v.transpose())[0][0] + aver_b
                q_row.append(result)
            self.q.append(q_row)
        return True

    # --- get Methods ---
    def get_size(self):
        return self.__img_size

    def get_filter_size(self):
        return self.__filter_radius * 2 + 1

    # 获取灰度结果图或一个通道上的图像，需要后期进行拼合
    def get_res_img(self):
        img = Image.new('L', self.origin_p.size)
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
        for i in range(3):
            self.__guide_v_buff[i] = util.calculate_box(self.guide_v[i])
            self.__pg_v_buff[i] = util.calculate_box(util.array_multiply(self.p, self.guide_v[i]))
            self.__guide2_v_buff[i] = util.calculate_box(util.array_multiply(self.guide_v[i], self.guide_v[i]))
        self.__guide_mix_v_buff[0] = util.calculate_box(util.array_multiply(self.guide_v[0], self.guide_v[1]))
        self.__guide_mix_v_buff[1] = util.calculate_box(util.array_multiply(self.guide_v[0], self.guide_v[2]))
        self.__guide_mix_v_buff[2] = util.calculate_box(util.array_multiply(self.guide_v[1], self.guide_v[2]))
        self.__p2_buff = util.calculate_box(util.array_multiply(self.p, self.p))
        self.__calculate_ab_buff()

    def __calculate_ab_buff(self):
        param_a_v, param_b = [[], [], []], []
        r = self.__filter_radius
        w, h = self.__img_size[0], self.__img_size[1]
        # a and b in padding positions are simply set to 0
        for i in range(r):
            for j in range(3):
                param_a_v[j].append([0.0 for k in range(self.__padding_img_size[0])])
            param_b.append([0 for k in range(self.__padding_img_size[0])])
        for i in range(r, r + h):
            tmp_a_row_v = [[0.0 for k in range(r)], [0.0 for k in range(r)], [0.0 for k in range(r)]]
            tmp_b_row = [0.0 for k in range(r)]
            # calculate a and b here
            for j in range(r, r + w):
                tmp_ab = self.__calculate_ab_at(i, j)
                for k in range(3):
                    tmp_a_row_v[k].append(tmp_ab[0][k])  # get a
                tmp_b_row.append(tmp_ab[1])  # get b
            for j in range(3):
                tmp_a_row_v[j] += [0.0 for z in range(r)]
                param_a_v[j].append(tmp_a_row_v[j])
            tmp_b_row += [0.0 for k in range(r)]
            param_b.append(tmp_b_row)
        for i in range(r + h, self.__padding_img_size[1]):
            for j in range(3):
                param_a_v[j].append([0.0 for k in range(self.__padding_img_size[0])])
            param_b.append([0 for k in range(self.__padding_img_size[0])])
        for i in range(3):
            self.__a_v_buff[i] = util.calculate_box(param_a_v[i])
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
        sum_p = util.calculate_sum(self.__p_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        aver_p = sum_p / float(w)
        sum_i_v = [0, 0, 0]  # sigma(gi)
        aver_i_v = [0, 0, 0]  # E(gi)
        aver_u_p_v = [0, 0, 0]  # uk * pk
        sum_i_p_v = [0, 0, 0]  # sigma(Ii * pi)
        a_member_v = [0, 0, 0]  # 暂存a计算公式中的分子
        for i in range(3):
            sum_i_v[i] = util.calculate_sum(self.__guide_v_buff[i], c[0][0], c[0][1], c[1][0], c[1][1])
            aver_i_v[i] = sum_i_v[i] / float(w)
            aver_u_p_v[i] = aver_i_v[i] * aver_p
            sum_i_p_v[i] = util.calculate_sum(self.__pg_v_buff[i], c[0][0], c[0][1], c[1][0], c[1][1])
            a_member_v[i] = sum_i_p_v[i] / float(w) - aver_u_p_v[i]
        cov_matrix = self.__calculate_covariance_matrix(c[0][0], c[0][1], c[1][0], c[1][1], aver_i_v)
        u_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        denominator = cov_matrix + u_matrix * self.__epsilon
        if np.linalg.det(denominator) == 0:
            # 矩阵不可逆
            a_res = (1, 1, 1)
        else:
            a_denominator_matrix = np.linalg.inv(denominator)
            a_mem_mat = np.array([[a_member_v[0], a_member_v[1], a_member_v[2]]]).transpose()
            res_mat = a_denominator_matrix.dot(a_mem_mat)
            a_res = (res_mat[0][0], res_mat[1][0], res_mat[2][0])
        tmp = np.array([aver_i_v]).dot(np.array([a_res]).transpose())
        b_res = aver_p - tmp[0][0]
        return a_res, b_res

    def __calculate_aver_ab_at(self, x, y):
        r = self.__filter_radius
        c = [
            [(x - r, y - r), (x - r, y + r)],
            [(x + r, y - r), (x + r, y + r)]
        ]
        sum_a = []
        w = self.get_filter_size() ** 2
        for i in range(3):
            tmp = util.calculate_sum(self.__a_v_buff[i], c[0][0], c[0][1], c[1][0], c[1][1])
            sum_a.append(tmp / float(w))
        sum_b = util.calculate_sum(self.__b_buff, c[0][0], c[0][1], c[1][0], c[1][1])
        return sum_a, sum_b / float(w)

    # 计算协方差矩阵，返回二维np.array
    def __calculate_covariance_matrix(self, lu, ru, lb, rb, aver_g_v):
        res = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        tmp2 = []
        tmp_mix = []  # g0g1, g0g2, g1g2
        for i in range(3):
            tmp2.append(util.calculate_sum(self.__guide2_v_buff[i], lu, ru, lb, rb))
            tmp_mix.append(util.calculate_sum(self.__guide_mix_v_buff[i], lu, ru, lb, rb))
            res[i][i] = tmp2[i] - aver_g_v[i] * aver_g_v[i]
        res[0][1] = tmp_mix[0] - aver_g_v[0] * aver_g_v[1]
        res[0][2] = tmp_mix[1] - aver_g_v[0] * aver_g_v[2]
        res[1][2] = tmp_mix[2] - aver_g_v[1] * aver_g_v[2]
        res[2][1], res[1][0], res[2][0] = res[1][2], res[0][1], res[0][2]
        return res
