# ===============================================================================
# Copyright 2018 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

import os
from copy import deepcopy

from fiona import collection
from fiona import open as fopen
from numpy import nan
from pandas import read_csv, concat


def attribute_shapefile(shp, *results):
    df = None
    s = None

    out = shp.replace('.shp', '_13JAN2020.shp')

    agri_schema = {'geometry': 'Polygon',
                   'properties': {
                       'OBJECTID': 'int',
                       'Supply': 'str',
                       'Acres': 'float',
                       'System': 'str',
                       'Crop': 'str',
                       'PIXELS': 'int'}}

    first = True
    print(results)
    for res in results[0]:
        year = int(res[-8:-4])
        c = read_csv(res)
        c['MONTH'][c['MONTH'] < 4] = nan
        c['MONTH'][c['MONTH'] > 10] = nan
        c.dropna(axis=0, how='any', inplace=True)
        c['ETR_MM'] *= 0.69
        c['ET_MM'] = c['ETR_MM'] * c['ETRF']
        
        c = c.groupby('OBJECTID').agg({'NDVI': 'mean',
                                       'ETRF': 'mean',
                                       'ETR_MM': 'sum',
                                       'ET_MM': 'sum',
                                       'PPT_MM': 'sum',
                                       'PIXELS': 'median'}).reset_index()

        renames = {'NDVI': 'NDVI_{}'.format(year),
                   'ETRF': 'ETRF_{}'.format(year),
                   'ETR_MM': 'ETR_{}'.format(year),
                   'ET_MM': 'ET_{}'.format(year),
                   'PPT_MM': 'PPT_{}'.format(year)}

        c.rename(columns=renames, inplace=True)

        if first:
            df = deepcopy(c)
            s = {int(r['OBJECTID']): int(r['PIXELS']) for i, r in c.iterrows()}
            first = False
        else:
            df.drop(columns=['PIXELS', 'OBJECTID'], axis=1, inplace=True)
            df = concat([df, c], join='outer', axis=1, sort=True)
            
        df.to_csv(out.replace('.shp', '.csv'))
        schema_dict = {'NDVI_{}'.format(year): 'float',
                       'ETRF_{}'.format(year): 'float',
                       'ETR_{}'.format(year): 'float',
                       'ET_{}'.format(year): 'float',
                       'PPT_{}'.format(year): 'float'}

        agri_schema['properties'].update(schema_dict)

    with fopen(shp, 'r') as src:
        print('writing', out)
        src_crs = src.crs
        src_driver = src.driver

        with collection(out, mode='w', driver=src_driver,
                        schema=agri_schema, crs=src_crs) as output:
            for rec in src:
                p = rec['properties']
                props = {'OBJECTID': p['OBJECTID'],
                         'Supply': p['Supply_Sou'],
                         'Acres': p['Acres'],
                         'System': p['System_Typ'],
                         'Crop': p['Crop_Type']}

                props.update(df[df['OBJECTID'] == p['OBJECTID']].to_dict('records')[0])
                props.update({'PIXELS': s[p['OBJECTID']]})
                props['OBJECTID'] = int(props['OBJECTID'])
                output.write({'geometry': rec['geometry'],
                              'properties': props,
                              'id': p['OBJECTID']})


if __name__ == '__main__':
    lolo = os.path.join('D:\\', 'pyMETRIC', 'lolo')
    s = os.path.join(lolo, 'study_area', 'Lolo_Project_Irrigation.shp')
    r = []
    for y in ['2014', '2015', '2016', '2018']:
        r.append(os.path.join(lolo, '{}'.format(y), 'ET', 'LINEAR_ZONES', 'monthly_zonal_stats_{}.csv'.format(y)))
    attribute_shapefile(s, r)
# ========================= EOF ====================================================================
