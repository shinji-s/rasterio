Error Handling
==============

.. todo::

    error enums, context managers, converting GDAL errors to python exceptions


Debugging internal GDAL functions
----------------------------------

To get more debugging information from the internal GDAL/PROJ code:

1. Enable the `CPL_DEBUG` config option.

    .. note:: If setting the :envvar:`PROJ_DEBUG` environment variable
              inside a Python script, make sure that it is set before
              importing rasterio.

    .. code-block:: python

        import os
        os.environ["PROJ_DEBUG"] = "2"

        import rasterio

        with rasterio.Env(CPL_DEBUG=True):
            ...


2. Activate logging in `rasterio` with the devel `DEBUG`:

    More information available here: https://docs.python.org/3/howto/logging.html

    Here are examples to get started.

    Example - Add handler to the `rasterio` logger:

    .. code-block:: python

        import logging

        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:%(message)s")
        console_handler.setFormatter(formatter)
        logger = logging.getLogger("rasterio")
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)


    Example - Activate default logging config:

    .. code-block:: python

        import logging

        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
