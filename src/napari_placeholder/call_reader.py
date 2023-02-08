# Test der Funktion _reader()
from _reader import reader_function
from napari_placeholder import Maldi_MS, napari_get_reader
from pathlib import Path

filename = '220912_KWS_PB_NEG_NEDC_7mg_newslide_kidneytissue_1pt88.imzML'
path1 = 'C:/Temp'
path2 = Path(path1, filename)

my_reader = napari_get_reader(path2)
maldi_ms = my_reader(path2)

# maldi_ms = reader_function(path2)

print('Number of spectra:', maldi_ms.get_num_spectra())
print('Coordinates:', maldi_ms.get_coordinates(34567))
# maldi_ms.print_metadata()
maldi_ms.plot_spectrum(34567)
