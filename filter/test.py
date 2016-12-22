import filter.GuidedFilter as filter


test = filter.GuideFilter()

test.read_img('../input/img_smoothing/cat.bmp')
test.set_guide('../input/img_smoothing/cat.bmp')
test.set_filter_radius(2)
test.run()
res = test.get_res_img()
if not (res is None):
    res.show()
    res.save('../output/img_smoothing/cat_output_2.bmp')
