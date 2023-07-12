import numpy as np
import os

# from napari_placeholder import write_single_image, write_multiple
from msi_explorer import write_metadata

# tmp_path is a pytest fixture
def test_metadata_writer(tmp_path):
    """Tests if we can write a csv file"""
    
    # create some fake data & filepath
    data = np.random.random([2,3])
    testfile = str(tmp_path / "myfile.csv")
    
    # write using our function
    write_metadata(testfile, data)
    
    assert os.path.isfile(testfile)
