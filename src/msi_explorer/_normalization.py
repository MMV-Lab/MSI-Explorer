"""
Provides preprocessing steps for spectra
"""

def normalize_tic(spectrum):
    """
    Runs total ion current normalization on a given spectrum
    
    Parameters
    ----------
    spectrum : list
        spectrum to normalize
        
    Returns
    -------
        list of same size, the normalized spectrum
    """
    mzs = spectrum[0]
    intensities = spectrum[1]
    length = len(intensities)
    sum_of_values = sum((abs(value) for value in intensities))
    if (sum_of_values > 0):
        new_spectrum = length * intensities / sum_of_values
        
    else:
        new_spectrum = [0] * length
    
    new_spectrum = [mzs, new_spectrum]
    return new_spectrum

def normalize_rms(spectrum):
    """
    Runs mean square normalization on a given spectrum
    
    Parameters
    ----------
    spectrum : list
        spectrum to normalize
        
    Returns
    -------
        list of same size, the normalized spectrum
    """
    import math, statistics
    mzs = spectrum[0]
    intensities = spectrum[1]
    quadratic_mean = math.sqrt(statistics.mean(intensities * intensities))
    if quadratic_mean > 0:
        new_spectrum = intensities / quadratic_mean
         
    else:
        new_spectrum = [0] * len(intensities)
        
    new_spectrum = [mzs, new_spectrum]
    return new_spectrum

def normalize_reference(spectrum, feature = 1):
    """
    Runs reference normalization on a given spectrum
    
    Parameters
    ----------
    spectrum : list
        spectrum to normalize
    feature : int
        index of the reference m/z
        
    Returns
    -------
        list of the same size, the normalized spectrum
    """
    # TODO: warn about missing feature
    mzs = spectrum[0]
    intensities = spectrum[1]
    reference = intensities[feature]
    if reference > 0:
        new_spectrum = intensities / reference
    
    else:
        # TODO: warn about bad reference (reference = 0)
        new_spectrum = [0] * len(intensities)
        
    new_spectrum = [mzs, new_spectrum]
    return new_spectrum
    
    
    
    
    
    
    
    