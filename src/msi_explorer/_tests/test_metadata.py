import pytest

from msi_explorer import MetadataWindow, napari_get_reader

FILENAME = "src/msi_explorer/_tests/data/Example_Processed.imzML"
reader = napari_get_reader(FILENAME)
maldi_data = reader(FILENAME)

@pytest.mark.metadata
def test_metadata_expansion_key():
    # Create metadata window
    print(1)
    my_window = MetadataWindow(maldi_data, None)
    print(2)
    # Fill "key" field of last line
    data_frame = my_window.layout().itemAt(0).widget()
    print(3)
    data_frame.cellWidget(data_frame.rowCount() - 1, 0).setText("Key")
    print(4)
    # Check if new line has been created
    assert data_frame.cellWidget(data_frame.rowCount() - 1, 0).text() != "Key"


def test_metadata_expansion_value():
    # Create metadata window
    my_window = MetadataWindow(maldi_data, None)

    # Fill "value" field of last line
    data_frame = my_window.layout().itemAt(0).widget()
    data_frame.cellWidget(data_frame.rowCount() - 1, 1).setText("Value")

    # Check if new line has been created
    assert (
        data_frame.cellWidget(data_frame.rowCount() - 1, 1).text() != "Value"
    )


def test_metadata_expansion_both():
    # Create metadata window
    my_window = MetadataWindow(maldi_data, None)

    # Fill "key" and "value" fields of last line
    data_frame = my_window.layout().itemAt(0).widget()
    row = data_frame.rowCount() - 1
    data_frame.cellWidget(row, 0).setText("Key")
    data_frame.cellWidget(row, 1).setText("Value")

    # Check if new line has been created
    row = data_frame.rowCount() - 1
    assert (
        data_frame.cellWidget(row, 0).text() != "Key"
        and data_frame.cellWidget(row, 1).text() != "Value"
    )
