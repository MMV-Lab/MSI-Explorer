# Test der Funktion _reader()
from _reader import reader_function
from _maldi_ms_data import Maldi_MS
from pathlib import Path

filename = '220912_KWS_PB_NEG_NEDC_7mg_newslide_kidneytissue_1pt88.imzML'
path1 = 'C:/Temp'
path2 = Path(path1, filename)

maldi_ms = reader_function(path2)

print('Number of spectra:', maldi_ms.get_num_spectra())
print('Coordinates:', maldi_ms.get_coordinates(34567))
# maldi_ms.print_metadata()
maldi_ms.plot_spectrum(34567)
