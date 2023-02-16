# pytest program for the class Maldi_MS in the module _maldi_ms_data.py
import numpy as np
from napari_placeholder import napari_get_reader

filename = 'src/napari_placeholder/_tests/data/Example_Processed.imzML'
my_reader = napari_get_reader(filename)
maldi_data = my_reader(filename)

def test_init():
    string = str(type(maldi_data))
    assert string == '<class \'napari_placeholder._maldi_ms_data.Maldi_MS\'>'

def test_get_num_spectra():
    n = maldi_data.get_num_spectra()
    assert n == 9

def test_get_coordinates():
    c = maldi_data.get_coordinates(4)
    assert c == (2, 2, 1)

def test_get_spectrum():
    s = maldi_data.get_spectrum(3)
    assert len(s[0]) == 8399
    assert len(s[1]) == 8399
    assert s[0][5] == 100.5

def test_get_metadata():
    metadata = maldi_data.get_metadata()
    assert metadata[6:27] == '"file_description": {'

def test_get_ion_image():
    image = maldi_data.get_ion_image(328.9, 0.25)
    image = image.round(3)
    image2 = np.array([[9.696, 6.044, 4.967], [7.814, 5.316, 2.866], \
        [1.663, 4.916, 4.576]])
    assert np.array_equal(image, image2)
