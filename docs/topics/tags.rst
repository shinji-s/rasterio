Tagging datasets and bands
==========================

GDAL's `data model <https://gdal.org/user/raster_data_model.html>`__ includes
collections of key, value pairs for major classes. In that model, these are
"metadata", but since they don't have to be just for metadata, these key, value
pairs are called "tags" in rasterio.

Reading tags
------------

I'm going to use the rasterio interactive inspector in these examples below.

.. code-block:: console

    $ rio insp tests/data/RGB.byte.tif
    Rasterio 1.2.0 Interactive Inspector (Python 3.7.8)
    Type "src.name", "src.read(1)", or "help(src)" for more information.
    >>> 

Tags belong to namespaces. To get a copy of a dataset's tags from the default
namespace, call :meth:`~.DatasetReader.tags` with no arguments.

.. code-block:: pycon

    >>> import rasterio
    >>> src = rasterio.open("tests/data/RGB.byte.tif")
    >>> src.tags()
    {'AREA_OR_POINT': 'Area'}

A dataset's bands may have tags, too. Here are the tags from the default namespace
for the first band, accessed using the positional band index argument of :meth:`~.DatasetReader.tags`.

.. code-block:: pycon

    >>> src.tags(1)['STATISTICS_MEAN']
    '29.947726688477'
    
These are the tags that came with the sample data I'm using to test rasterio. In
practice, maintaining stats in the tags can be unreliable as there is no automatic
update of the tags when the band's image data changes.

The 3 standard, non-default GDAL tag namespaces are 'SUBDATASETS', 'IMAGE_STRUCTURE', 
and 'RPC'. You can get the tags from these namespaces using the `ns` keyword of
:meth:`~.DatasetReader.tags`.

.. code-block:: pycon

    >>> src.tags(ns='IMAGE_STRUCTURE')
    {'INTERLEAVE': 'PIXEL'}
    >>> src.tags(ns='SUBDATASETS')
    {}
    >>> src.tags(ns='RPC')
    {}

.. note::

A special case for GDAL tag namespaces are those prefixed with 'xml' e.g. 'xml:TRE' or 'xml:VRT'. 
GDAL will treat these namespaces as a single xml string.

Writing tags
------------

You can add new tags to a dataset or band, in the default or another namespace,
using the :meth:`~.DatasetWriter.update_tags` method. Unicode tag values, too, at least for TIFF
files.

.. code-block:: python
    
    import rasterio

    with rasterio.open(
            '/tmp/test.tif', 
            'w', 
            driver='GTiff', 
            count=1, 
            dtype=rasterio.uint8, 
            width=10, 
            height=10) as dst:

        dst.update_tags(a='1', b='2')
        dst.update_tags(1, c=3)
        with pytest.raises(ValueError):
            dst.update_tags(4, d=4)
        
        # True
        assert dst.tags() == {'a': '1', 'b': '2'}
        # True
        assert dst.tags(1) == {'c': '3' }
        
        dst.update_tags(ns='rasterio_testing', rus=u'другая строка')
        # True
        assert dst.tags(ns='rasterio_testing') == {'rus': u'другая строка'}

As with image data, tags aren't written to the file on disk until the dataset
is closed.
