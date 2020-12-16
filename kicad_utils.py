import pcbnew
from utils import pose_to_xyr


def kicad_polygon(geom):
    points = geom.exterior.coords
    for (x1, y1), (x2, y2) in [(points[i], points[(i + 1) % len(points)])
                               for i in range(len(points))]:
        seg = pcbnew.PCB_SHAPE()
        seg.SetStart(pcbnew.wxPointMM(x1, y1))
        seg.SetEnd(pcbnew.wxPointMM(x2, y2))
        seg.SetLayer(pcbnew.Edge_Cuts)
        yield seg

    for interior in geom.interiors:
        points = interior.coords
        for (x1, y1), (x2, y2) in [(points[i], points[(i + 1) % len(points)])
                                   for i in range(len(points))]:
            seg = pcbnew.PCB_SHAPE()
            seg.SetShape(pcbnew.S_SEGMENT)
            seg.SetStart(pcbnew.wxPointMM(x1, y1))
            seg.SetEnd(pcbnew.wxPointMM(x2, y2))
            seg.SetLayer(pcbnew.Edge_Cuts)
            yield seg


def kicad_text(p, text, size=pcbnew.FromMM(1.27), layer=pcbnew.F_SilkS):
    x, y, r = pose_to_xyr(p)
    item = pcbnew.PCB_TEXT(None)
    item.SetPosition(pcbnew.wxPointMM(x, y))
    item.SetTextAngle(r * 10)
    item.SetLayer(layer)
    item.SetText(text)
    item.SetTextSize(pcbnew.wxSize(size, size))
    if layer == pcbnew.B_SilkS:  # all mirrored layers?
        item.SetMirrored(True)  #item.Flip(pcbnew.wxPointMM(x, y), False)
    return item


def kicad_circle(p, diameter, layer=pcbnew.Edge_Cuts):
    x, y = p.x, p.y
    item = pcbnew.PCB_SHAPE()
    item.SetShape(pcbnew.S_CIRCLE)
    item.SetStart(pcbnew.wxPointMM(x, y))
    item.SetEnd(pcbnew.wxPointMM(x + diameter / 2, y))
    item.SetLayer(layer)
    return item
