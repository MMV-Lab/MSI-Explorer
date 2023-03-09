# pytest program for the class Maldi_MS in the module _maldi_ms_data.py
import numpy as np
from napari_placeholder import napari_get_reader

filename = 'src/napari_placeholder/_tests/data/Example_Processed.imzML'
reader_function = napari_get_reader(filename)
maldi_ms = reader_function(filename)

def test_init():
    type1 = str(type(maldi_ms))
    assert type1 == '<class \'napari_placeholder._maldi_ms_data.Maldi_MS\'>'

def test_check_i():
    i = maldi_ms.check_i(23)
    assert i == 8

def test_get_spectrum():
    spec = maldi_ms.get_spectrum(3)
    assert len(spec[0]) == 8399
    assert len(spec[1]) == 8399
    assert spec[0][5] == 100.5

def test_get_index():
    index = maldi_ms.get_index(2, 2)
    assert index == 4

def test_get_coordinates():
    coord = maldi_ms.get_coordinates(4)
    assert coord == (2, 2, 1)

def test_get_metadata_json():
    meta = maldi_ms.get_metadata_json()
    assert meta[6:27] == '"file_description": {'

def test_get_num_spectra():
    num = maldi_ms.get_num_spectra()
    assert num == 9

def test_get_ion_image():
    image = maldi_ms.get_ion_image(328.9, 0.25)
    image = image.round(3)
    image2 = np.array([[9.696, 6.044, 4.967], \
                       [7.814, 5.316, 2.866], \
                       [1.663, 4.916, 4.576]])
    assert np.array_equal(image, image2)

def test_get_tic():
    tic = maldi_ms.get_tic()
    tic1 = tic[:4]
    tic1 = tic1.round(3)
    tic2 = np.array([121.850, 182.318, 161.809, 200.963])
    assert np.array_equal(tic1, tic2)

def test_get_metadata():
    meta = maldi_ms.get_metadata()
    assert meta['pixel size x'] == 100.0

def test_calc_mean_spec():
    spec = maldi_ms.calc_mean_spec(9)
    mz1 = spec[0][5:10]
    mz1 = mz1.round(3)
    mz2 = np.asarray([101., 101.083, 101.167, 101.25, 101.333], dtype=np.float32)
    assert np.array_equal(mz1, mz2)

    intens1 = spec[1][70:75]
    intens1 = intens1.round(3)
    intens2 = np.asarray([2.918, 2.466, 1.452, 0.654, 0.129], dtype=np.float64)
    assert np.array_equal(intens1, intens2)
