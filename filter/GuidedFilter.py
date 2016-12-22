from PIL import Image

import filter.util as util


class GuideFilter(object):
    def __init__(self):
        self.p = None  # source image matrix, padded after set_filter_radius()
        self.guide = None  # guide image matrix, padded after set_filter_radius()
        self.q = None  # target image matrix, padded after set_filter_radius()
        self.__p_buff = None  # box filter method buffer
        self.__guide_buff = None  # box filter method buffer
        self.__pg_buff = None  # box filter method buffer
        self.__p2_buff = None  # box filter method buffer
        self.__img_size = None  # source size, (width, height)
        self.__filter_radius = None  # filter radius

    # --- init methods ---
    def read_img(self, img_path):
        img = Image.open(img_path)
        self.p = util.list_to_matrix(list(img.getdata()), img.width, img.height)
        self.__img_size = img.size

    def set_guide(self, guide_path):
        img = Image.open(guide_path)
        # guide size should be equal to source size
        if img.size == self.__img_size:
            self.guide = util.list_to_matrix(list(img.getdata()), img.width, img.height)
        else:
            # error happens
            print('> Error: guide\'s size should be equal to source\'s size')
            return

    def set_filter_radius(self, r):
        self.__filter_radius = r
        self.p = util.padding(self.p, r - 1)
        self.guide = util.padding(self.guide, r - 1)

    # --- kernel algorithm ---
    def run(self):
        self.__calculate_buff()
        if self.p is None or self.guide is None or self.q is None:
            return False
        return True

    # --- get Methods ---
    def get_size(self):
        return self.__img_size

    def get_filter_size(self):
        return self.__filter_radius * 2 - 1

    def get_res_img(self):
        img = Image.new('L', self.__img_size)
        if self.q is None:
            print('> Error: Algorithm has not finished')
            img.putdata(util.matrix_to_list(self.p))
        else:
            img.putdata(util.matrix_to_list(self.q))
        return img

    # --- internal methods, used to implement the kernel algorithm ---
    def __calculate_buff(self):
        self.__p_buff = util.calculate_box(self.p)
        self.__guide_buff = util.calculate_box(self.guide)
        self.__pg_buff = util.calculate_box(util.array_multiply(self.p, self.guide))
        self.__p2_buff = util.calculate_box(util.array_multiply(self.p, self.p))
