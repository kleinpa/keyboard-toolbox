"""Tools for working with dxf (vector CAD) files."""

import ezdxf
import io


def polygon_to_dxf_file(geom):
    """Build a .dxf file containing a single Shapely polygon."""
    doc = ezdxf.new()
    doc.header['$INSUNITS'] = 4  # Milimeters
    doc.header['$AUNITS'] = 0  # Degrees
    doc.header['$MEASUREMENT'] = 1  # Measurement Metric

    msp = doc.modelspace()
    msp.add_lwpolyline(geom.exterior.coords)
    for interior in geom.interiors:
        msp.add_lwpolyline(interior.coords)

    fn = io.StringIO()
    doc.write(fn, fmt="asc")
    return fn.getvalue().encode('utf-8')
