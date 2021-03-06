# Licensed under a 3-clause BSD style license - see LICENSE.rst

from astropy import coordinates

coordsys_name_mapping = dict(zip(coordinates.frame_transform_graph.get_names(),
                                 coordinates.frame_transform_graph.get_names()))
coordsys_name_mapping['ecliptic'] = 'geocentrictrueecliptic' # needs expert attention TODO


def objects_to_ds9_string(obj_list, coordsys='fk5', fmt='.4f', radunit='deg'):
    """Take a list of regions and generate ds9 region strings"""

    ids = {"<class 'regions.shapes.circle.CircleSkyRegion'>": 'skycircle',
           "<class 'regions.shapes.circle.CirclePixelRegion'>": 'pixcircle',
           "<class 'regions.shapes.ellipse.EllipseSkyRegion'>": 'skyellipse',
           "<class 'regions.shapes.ellipse.EllipsePixelRegion'>": 'pixellipse',
           "<class 'regions.shapes.polygon.PolygonSkyRegion'>": 'skypolygon',
           "<class 'regions.shapes.polygon.PolygonPixelRegion'>": 'pixpolygon'}

    if radunit == 'arcsec':
        if coordsys in coordsys_name_mapping.keys():
            radunitstr = '"'
        else:
            raise ValueError('Radius unit arcsec not valid for coordsys {}'.format(coordsys))
    else:
        radunitstr = ''

    ds9_strings = {'circle': 'circle({x:'+fmt+'},{y:'+fmt+'},{r:'+fmt+'}'+radunitstr+')\n',
                   'ellipse': 'ellipse({x:'+fmt+'},{y:'+fmt+'},{r1:'+fmt+'}'+radunitstr+',{r2:'+fmt+'}'+radunitstr+',{ang:'+fmt+'})\n',
                   'polygon': 'polygon({c})\n'}

    output = '# Region file format: DS9 astropy/regions\n'
    output += '{}\n'.format(coordsys)

    for reg in obj_list:
        temp = str(reg.__class__)
        if temp in ids.keys():
            t = ids[temp]
            if t == 'skycircle':
                # TODO: Why is circle.center a list of SkyCoords?
                x = reg.center.transform_to(coordsys).spherical.lon.to('deg').value[0]
                y = reg.center.transform_to(coordsys).spherical.lat.to('deg').value[0]
                r = reg.radius.to(radunit).value
                output += ds9_strings['circle'].format(**locals())
            elif t == 'pixcircle':
                # TODO: Why is circle.center a list of SkyCoords?
                x = reg.center.x
                y = reg.center.y
                r = reg.radius
                output += ds9_strings['circle'].format(**locals())
            elif t == 'skyellipse':
                x = reg.center.transform_to(coordsys).spherical.lon.to('deg').value[0]
                y = reg.center.transform_to(coordsys).spherical.lat.to('deg').value[0]
                r2 = reg.major.to(radunit).value
                r1 = reg.minor.to(radunit).value
                ang = reg.angle.to('deg').value
                output += ds9_strings['ellipse'].format(**locals())
            elif t == 'pixellipse':
                x = reg.center.x
                y = reg.center.y
                r2 = reg.major
                r1 = reg.minor
                ang = reg.angle
                output += ds9_strings['ellipse'].format(**locals())
            elif t == 'skypolygon':
                v = reg.vertices.transform_to(coordsys)
                coords = [(x.to('deg').value, y.to('deg').value) for x, y in
                          zip(v.spherical.lon, v.spherical.lat)]
                val = "{:"+fmt+"}"
                temp = [val.format(x) for _ in coords for x in _]
                c = ",".join(temp)
                output += ds9_strings['polygon'].format(**locals())
            elif t == 'pixpolygon':
                v = reg.vertices
                coords = [(x, y) for x, y in zip(v.x, v.y)]
                val = "{:"+fmt+"}"
                temp = [val.format(x) for _ in coords for x in _]
                c = ",".join(temp)
                output += ds9_strings['polygon'].format(**locals())

    return output


def write_ds9(obj_list, filename='ds9.reg', coordsys='fk5'):
    """Write ds9 region file"""
    output = objects_to_ds9_string(obj_list, coordsys)
    with open(filename, 'w') as fh:
        fh.write(output)
