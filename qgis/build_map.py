import os
import shutil
import re
import lxml.etree as et
from unicodedata import normalize

COLD = '/media/research/IrrigationGIS/upper_yellowstone/cold.shp'
HOT = '/media/research/IrrigationGIS/upper_yellowstone/hot.shp'
FIELDS = '/media/research/IrrigationGIS/openET/MT/statewide_water_plan_sid.shp'


def paste_pixel_points(dest):
    point_src = os.path.dirname(HOT)

    for p in ['hot', 'cold']:
        _src = [os.path.join(point_src, x) for x in os.listdir(point_src) if p in os.path.basename(x)]
        _dst = [os.path.join(dest, 'PIXELS',  x) for x in os.listdir(point_src) if p in os.path.basename(x)]

        [shutil.copyfile(s, d) for s, d in zip(_src, _dst)]


def modify_qgs(template, input_loc):
    sources = {'cold': os.path.join(input_loc, 'PIXELS', 'cold.shp'),
               'hot': os.path.join(input_loc, 'PIXELS', 'hot.shp'),
               'statewide_water_plan_sid': '/media/research/IrrigationGIS/openET/MT/statewide_water_plan_sid.shp',
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
    print('wrote {}'.format(output))


if __name__ == '__main__':
    home = os.path.expanduser('~')
    for year in [2016, 2017, 2018]:
        path = os.path.join('/media/research/IrrigationGIS/upper_yellowstone/metric/{}'.format(year))
        template = '/media/research/IrrigationGIS/upper_yellowstone/qgs_template.qgs'
        targets = []
        path_rows = ['p038r028', 'p038r029', 'p039r028', 'p039r029']
        for pr in path_rows:
            rt = os.path.join(path, pr)
            images = [os.path.join(rt, x) for x in os.listdir(rt) if os.path.isdir(os.path.join(rt, x))]
            missing = [x for x in images if 'PIXELS' not in os.listdir(x)]
            for i in images:
                # paste_pixel_points(i)
                modify_qgs(template, i)
# ========================= EOF ===================================================
