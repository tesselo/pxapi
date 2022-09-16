import numpy
from pixels.mosaic import first_valid_pixel
from wmts.algebra import parser


def test_algebra(self):
    # Test regular latest pixel.
    bands = ["B01", "B02"]
    creation_args, first_end_date, stack = first_valid_pixel(
        self.geojson,
        end_date="2020-02-01",
        scale=500,
        bands=bands,
        clip=False,
        platforms="SENTINEL_2",
        maxcloud=100,
    )
    ndvi = parser.evaluate("(B01 + 2 * B02) / (B01 + B02)", bands, stack)
    expected = [[1.5, 1.5], [1.5, 1.5]]
    numpy.testing.assert_array_equal(ndvi, expected)
