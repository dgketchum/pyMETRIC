import os
import shutil
import re
import lxml.etree as et
from unicodedata import normalize

PIXELS = '/media/research/IrrigationGIS/teton/PIXELS'


def copytree(src, dst):
    for item in os.listdir(src):
        d = os.path.join(dst, item)
        # if os.path.isfile(d):
        #     try:
        #         os.remove(d)
        #     except FileNotFoundError:
        #         pass
        if not os.path.isdir(dst):
            os.mkdir(dst)
        s = os.path.join(src, item)
        shutil.copyfile(s, d, follow_symlinks=False)


def modify_qgs(template, input_loc, fields):
    sources = {'cold': os.path.join(input_loc, 'PIXELS', 'cold.shp'),
               'hot': os.path.join(input_loc, 'PIXELS', 'hot.shp'),
               'fields': fields,
               'hot_pixel_suggestion': os.path.join(input_loc, 'PIXEL_REGIONS',
                                                    'hot_pixel_suggestion.img'),
               'cold_pixel_suggestion': os.path.join(input_loc, 'PIXEL_REGIONS',
                                                     'cold_pixel_suggestion.img'),
               'region_mask': os.path.join(input_loc, 'PIXEL_REGIONS', 'region_mask.img'),
               'ndvi_toa': os.path.join(input_loc, 'INDICES', 'ndvi_toa.img'),
               'ts': os.path.join(input_loc, 'ts.img'),
               'albedo_at_sur': os.path.join(input_loc, 'albedo_at_sur.img'),
               'et_rf': os.path.join(input_loc, 'ETRF', 'et_rf.img')}

    with open(template) as _file:
        tree = et.parse(_file)
        txt = tree.xpath("//maplayer/datasource[contains(text(), 'albedo_at_sur.img')]")[0].text

        for key, val in sources.items():

            items = tree.xpath("//qgis/layer-tree-group/layer-tree-layer[@name='{}']".format(key))
            for s in items:
                s.attrib['source'] = val
            # trying to replace maplayer datasource
            tree.xpath("//maplayer/datasource[contains(text(), 'cold.shp')]")[0].text = sources['cold']
            tree.xpath("//maplayer/datasource[contains(text(), 'hot.shp')]")[0].text = sources['hot']

        string = et.tostring(tree, encoding=str)
        rep = str(os.path.dirname(txt))
        inp = str(input_loc).replace('\\', '/')
        string = re.sub(r"{}".format(rep), r"%s" % inp, string)

    output = os.path.join(input_loc, '{}_calbration_map.qgs'.format(os.path.basename(input_loc)))
    with open(output, 'w') as out_file:
        for line in string.splitlines():
            out_file.write(line)
    print('{}'.format(output))


if __name__ == '__main__':
    home = os.path.expanduser('~')
    map_count = 0
    field_bounds = '/media/research/IrrigationGIS/upper_yellowstone/metric/study_area/uy_fields_all.shp'
    template = '/media/research/IrrigationGIS/teton/qgs_template.qgs'
    for year in [2015, 2016, 2019]:
        path = os.path.join('/media/research/IrrigationGIS/teton/metric/{}'.format(year))
        targets = []
        path_rows = ['p039r027', 'p040r027']
        for pr in path_rows:
            rt = os.path.join(path, pr)
            images = [os.path.join(rt, x) for x in os.listdir(rt) if os.path.isdir(os.path.join(rt, x))]
            missing = [x for x in images if 'PIXELS' not in os.listdir(x)]
            for i in images:
                copytree(PIXELS, os.path.join(i, 'PIXELS'))
                modify_qgs(template, i, field_bounds)
                map_count += 1
    print('made {} maps'.format(map_count))
# ========================= EOF ===================================================
