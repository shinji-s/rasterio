Vector Features
===============

Rasterio's ``features`` module provides functions to extract shapes of raster
features and to create new features by "burning" shapes into rasters:
:func:`.shapes` and :func:`.rasterize`. These functions expose GDAL functions in
a general way, using iterators over GeoJSON-like Python objects instead of
GIS layers.

Extracting shapes of raster features
------------------------------------

Consider the Python logo.

.. image:: https://farm8.staticflickr.com/7018/13547682814_f2e459f7a5_o_d.png

The shapes of the foreground features can be extracted like this:

.. code-block:: python

    import pprint
    import rasterio
    from rasterio import features

    with rasterio.open('13547682814_f2e459f7a5_o_d.png') as src:
        blue = src.read(3)
   
    # pprint requires that the image dtype must be one of: int16, int32, uint8, uint16, float32.
    # If your data comes as int8 you can cast your data to an appropriate dtype like this: 
    # data = data.astype('int16')
    
    mask = blue != 255
    shapes = features.shapes(blue, mask=mask)
    pprint.pprint(next(shapes))

    # Output
    # pprint.pprint(next(shapes))
    # ({'coordinates': [[(71.0, 6.0),
    #                    (71.0, 7.0),
    #                    (72.0, 7.0),
    #                    (72.0, 6.0),
    #                    (71.0, 6.0)]],
    #   'type': 'Polygon'},
    # 253)

The shapes iterator yields ``geometry, value`` pairs. The second item is the
value of the raster feature corresponding to the shape and the first is its
geometry.  The coordinates of the geometries in this case are in pixel units
with origin at the upper left of the image. If the source dataset was
georeferenced, you would get similarly georeferenced geometries like this:

.. code-block:: python

    shapes = features.shapes(blue, mask=mask, transform=src.transform)

Burning shapes into a raster
----------------------------

To go the other direction, use :func:`.rasterize` to burn values into the pixels
intersecting with geometries.

.. code-block:: python

    image = features.rasterize(
                ((g, 255) for g, v in shapes),
                out_shape=src.shape)

By default, only pixels whose center is within the polygon or that
are selected by Bresenham's line algorithm will be burned in.  
You can specify ``all_touched=True`` to burn in all pixels touched by the geometry.
The geometries will be rasterized by the "painter's algorithm" - 
geometries are handled in order and later geometries will overwrite earlier values.

Again, to burn in georeferenced shapes, pass an appropriate transform for the
image to be created.

.. code-block:: python

    image = features.rasterize(
                ((g, 255) for g, v in shapes),
                out_shape=src.shape,
                transform=src.transform)

The values for the input shapes are replaced with ``255`` in a generator
expression. Areas not covered by input geometries are replaced with an
optional ``fill`` value, which defaults to ``0``. The resulting image,
written to disk like this,

.. code-block:: python

    with rasterio.open(
            '/tmp/rasterized-results.tif', 'w', 
            driver='GTiff', 
            dtype=rasterio.uint8, 
            count=1, 
            width=src.width, 
            height=src.height) as dst:
        dst.write(image, indexes=1)

has a black background and white foreground features.

.. image:: https://farm4.staticflickr.com/3728/13547425455_79bdb5eaeb_o_d.png

