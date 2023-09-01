from msi_explorer import napari_get_reader


# tmp_path is a pytest fixture
def test_reader(tmp_path):
    """An example of how you might test your plugin."""

    # write some fake data using your supported file format
    my_test_file = str(tmp_path / "myfile.imzML")
    f = open(my_test_file, "a")
    f.write("Testtext")
    f.close()

    # try to read it back in
    reader = napari_get_reader(my_test_file)
    assert callable(reader)

def test_get_reader_pass():
    reader = napari_get_reader("fake.file")
    assert reader is None
