#import numpy as np

from msi_explorer import MSI_Explorer


def test_msi_explorer(make_napari_viewer):
    ### Tests if main widget & selection window can be created
    # make viewer
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    try:
        my_widget = MSI_Explorer(viewer)
    except:
        assert False
    assert True

def test_metadata(make_napari_viewer):
    ### Tests if metadata window can be created
    
    viewer = make_napari_viewer()
    
    my_widget = MSI_Explorer(viewer)
    try:
        my_widget._open_metadata()
    except:
        assert False
    assert True

    """# read captured output and check that it's as we expected
    captured = capsys.readouterr()
    assert captured.out == "napari has 1 layers\n" """

