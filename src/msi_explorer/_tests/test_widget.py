from msi_explorer import MSI_Explorer


def test_msi_explorer(make_napari_viewer):
    ### Tests if main widget & selection window can be created
    # make viewer
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    MSI_Explorer(viewer)
    assert True


def test_metadata(make_napari_viewer):
    ### Tests if metadata window can be created

    viewer = make_napari_viewer()

    my_widget = MSI_Explorer(viewer)
    my_widget.open_metadata()
    assert True
