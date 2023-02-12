"""Profile tests"""

import pickle

import pytest

import rasterio
from rasterio.profiles import Profile, DefaultGTiffProfile
from rasterio.profiles import default_gtiff_profile


def test_base_profile():
    assert 'driver' not in Profile()


def test_base_profile_kwarg():
    assert Profile(foo='bar')['foo'] == 'bar'


def test_gtiff_profile_interleave():
    assert DefaultGTiffProfile()['interleave'] == 'band'


def test_gtiff_profile_tiled():
    assert DefaultGTiffProfile()['tiled'] is True


def test_gtiff_profile_blockxsize():
    assert DefaultGTiffProfile()['blockxsize'] == 256


def test_gtiff_profile_blockysize():
    assert DefaultGTiffProfile()['blockysize'] == 256


def test_gtiff_profile_compress():
    assert DefaultGTiffProfile()['compress'] == 'lzw'


def test_gtiff_profile_nodata():
    assert DefaultGTiffProfile()['nodata'] == 0


def test_gtiff_profile_dtype():
    assert DefaultGTiffProfile()['dtype'] == rasterio.uint8


def test_gtiff_profile_other():
    assert DefaultGTiffProfile(count=3)['count'] == 3


def test_gtiff_profile_dtype_override():
    assert DefaultGTiffProfile(dtype='uint16')['dtype'] == rasterio.uint16


def test_open_with_profile(tmpdir):
    tiffname = str(tmpdir.join('foo.tif'))
    profile = default_gtiff_profile.copy()
    profile.update(count=1, width=256, height=256)
    with rasterio.open(tiffname, 'w', **profile) as dst:
        assert not dst.closed


def test_profile_overlay(path_rgb_byte_tif):
    with rasterio.open(path_rgb_byte_tif) as src:
        kwds = src.profile
    kwds.update(**default_gtiff_profile)
    assert kwds['tiled']
    assert kwds['compress'] == 'lzw'
    assert kwds['count'] == 3


def test_dataset_profile_property_tiled(data):
    """An tiled dataset's profile has block sizes"""
    with rasterio.open('tests/data/shade.tif') as src:
        assert src.profile['blockxsize'] == 256
        assert src.profile['blockysize'] == 256
        assert src.profile['tiled'] is True


def test_dataset_profile_property_untiled(data, path_rgb_byte_tif):
    """An untiled dataset's profile has block y sizes"""
    with rasterio.open(path_rgb_byte_tif) as src:
        assert 'blockxsize' not in src.profile
        assert src.profile['blockysize'] == 3
        assert src.profile['tiled'] is False


def test_dataset_convert_untiled_to_tiled(tmp_path, path_rgb_byte_tif):
    with rasterio.open(path_rgb_byte_tif) as src:
        assert 'blockxsize' not in src.profile
        assert src.profile['blockysize'] == 3
        assert src.profile['tiled'] is False

        dst_profile = src.profile
        dst_profile.update(tiled=True)
        with rasterio.open(tmp_path / 'test_tiled.tif', 'w+', **dst_profile) as dst_ds:
            assert dst_ds.profile['tiled'] is True
            assert dst_ds.profile['blockysize'] == 256
            assert dst_ds.profile['blockxsize'] == 256
            dst_ds.write(src.read(1), 1)


def test_profile_affine_set():
    """TypeError is raised on set of affine item"""
    profile = Profile()
    profile['transform'] = 'foo'
    with pytest.raises(TypeError):
        profile['affine'] = 'bar'


def test_profile_pickle():
    """Standard profile can be pickled"""
    assert pickle.loads(pickle.dumps(DefaultGTiffProfile())) == DefaultGTiffProfile()


def test_dataset_profile_pickle(path_rgb_byte_tif):
    """Dataset profiles can be pickled"""
    with rasterio.open(path_rgb_byte_tif) as src:
        assert pickle.loads(pickle.dumps(src.profile)) == src.profile
