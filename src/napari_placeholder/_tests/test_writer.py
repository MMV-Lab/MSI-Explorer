import numpy as np
import os

# from napari_placeholder import write_single_image, write_multiple
from napari_placeholder import metadata_writer

# tmp_path is a pytest fixture
def test_metadata_writer(tmp_path):
    """"Tests if we can write a csv file"""
    
    # createsome fake data & filepath
    data = np.random(5)
    testfile = str(tmp_path / "myfile.csv")
    
    # write using our function
    metadata_writer(testfile, data)
    
    assert os.path.isfile(testfile)
