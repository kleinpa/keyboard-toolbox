import ezdxf
import io


def shape_to_dxf_file(geom):
    doc = ezdxf.new()
    doc.header['$INSUNITS'] = 4  # Milimeters
    doc.header['$AUNITS'] = 0  # Degrees
    doc.header['$MEASUREMENT'] = 1  # Measurement Metric
    msp = doc.modelspace()

    msp.add_lwpolyline(geom.exterior.coords)

    for interior in geom.interiors:
        msp.add_lwpolyline(interior.coords)

    fn = io.TextIOWrapper(io.BytesIO())
    doc.write(fn, fmt="asc")
    fn.seek(0)
    return fn.detach()
