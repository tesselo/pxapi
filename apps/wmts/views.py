import datetime
import io
import os

import mercantile
import numpy
import rasterio
from django.http import HttpResponse
from pixels.mosaic import latest_pixel
from rest_framework.decorators import api_view
from tsuser.const import GET_QUERY_PARAMETER_AUTH_KEY
from wmts import const, wmts


@api_view(["GET"])
def wmtsview(request):
    """
    WMTS endpoint with monthly latest pixel layers.
    """
    # Get auth key.
    key = request.GET.get(GET_QUERY_PARAMETER_AUTH_KEY, None)
    # Get cloud cover query argument.
    max_cloud_cover_percentage = request.GET.get("max_cloud_cover_percentage", 100)
    # Construct base url for app.
    host = request.get_host()
    protocol = "http" if host in ["127.0.0.1:8000", "localhost"] else "https"
    urlbase = "{}://{}".format(protocol, host)
    # Generate WMTS xml.
    xml = wmts.gen(key, urlbase, max_cloud_cover_percentage)
    # Return xml to user.
    return HttpResponse(xml, content_type="text/xml")


@api_view(["GET"])
def tilesview(request, z, x, y, platform=""):
    """
    TMS tiles endpoint.
    """
    # Check for minimum zoom.
    if z < const.PIXELS_MIN_ZOOM:
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, "assets/tesselo_zoom_in_more.png")
        return HttpResponse(open(path, "rb"), content_type="image/png")

    # Retrieve end date from query args.
    end = request.GET.get("end")
    if not end:
        end = str(datetime.datetime.now().date())
    # Get cloud cover filter.
    max_cloud_cover_percentage = int(request.GET.get("max_cloud_cover_percentage", 100))
    # Compute tile bounds and scale.
    bounds = mercantile.xy_bounds(x, y, z)
    scale = abs(bounds[3] - bounds[1]) / const.TILE_SIZE
    geojson = {
        "type": "FeatureCollection",
        "crs": {"init": "EPSG:3857"},
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [bounds[0], bounds[1]],
                            [bounds[2], bounds[1]],
                            [bounds[2], bounds[3]],
                            [bounds[0], bounds[3]],
                            [bounds[0], bounds[1]],
                        ]
                    ],
                },
            }
        ],
    }
    # Specify the platform to use.
    platform = platform.upper()
    level = None
    if platform == "LANDSAT_4":
        bands = ["B3", "B2", "B1"]
        scaling = 255
    elif platform == "LANDSAT_5" or end < "2000-01-01":
        platform = ["LANDSAT_4", "LANDSAT_5"]
        bands = ["B3", "B2", "B1"]
        scaling = 255
    elif platform == "LANDSAT_7" or end < "2014-01-01":
        platform = ["LANDSAT_7"]
        bands = ["B3", "B2", "B1"]
        scaling = 255
    elif platform == "LANDSAT_8" or end < "2018-01-01":
        platform = ["LANDSAT_8"]
        bands = ["B4", "B3", "B2"]
        scaling = 30000
    else:
        platform = ["SENTINEL_2"]
        bands = ["B04", "B03", "B02"]
        scaling = 4000
        level = "L2A"
    # Get pixels.
    creation_args, date, stack = latest_pixel(
        geojson,
        end,
        scale,
        bands=bands,
        platforms=platform,
        limit=10,
        clip=False,
        pool=True,
        maxcloud=max_cloud_cover_percentage,
        level=level,
    )
    # Convert stack to image array in uint8.
    img = numpy.array(
        [255 * (numpy.clip(dat, 0, scaling) / scaling) for dat in stack]
    ).astype("uint8")
    # Prepare PNG output parameters.
    creation_args.update(
        {
            "driver": "PNG",
            "dtype": "uint8",
            "count": 3,
        }
    )
    # Write data to PNG BytesIO buffer.
    output = io.BytesIO()
    with rasterio.io.MemoryFile() as memfile:
        with memfile.open(**creation_args) as dst:
            dst.write(img)
        memfile.seek(0)
        output.write(memfile.read())

    # Send file buffer.
    output.seek(0)
    return HttpResponse(output, content_type="image/png")
