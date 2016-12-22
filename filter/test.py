import filter.GuidedFilter as filter

from filter.util import array_multiply, calculate_box, calculate_sum

test = filter.GuideFilter()
test.read_img('../input/img_smoothing/cat.bmp')
test.set_guide('../input/img_smoothing/cat.bmp')
test.set_filter_radius(8)  # means a 5 * 5 filter
test.set_epsilon(0.4 * 0.4)
test.run()
res = test.get_res_img()
if not (res is None):
    # res.show()
    res.save('../output/img_smoothing/cat_output_2.bmp')
print(test.count)
