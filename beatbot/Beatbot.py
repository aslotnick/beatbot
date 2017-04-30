import numpy 
from scipy.io import wavfile
from scipy.signal import find_peaks_cwt
from matplotlib.mlab import specgram
from matplotlib import pyplot

ONSET_WIDTH = 2000

class Beatbot(object):
    """
    Input some audio
    Detect the onsets
    For each "note", determine frequencies
    Cluster notes
    Each cluster is an "instrument"
    """

    def __init__(self, path, num_samples=None):
        self._load_audio(path, num_samples)
        self.absolute_samples = numpy.absolute(self.samples)
        self._onsets = []


    @property
    def onsets(self):
        """
        return the sample indices of onsets
        """
        if len(self._onsets) == 0:
            self._identify_changes()
            self._combine_onsets()
        return self._onsets


    @property
    def instrument_count(self):
        return 1
    

    def plot_onsets(self, path):
        """
        save a graph of the frequency with onsets 
        """
        pyplot.plot(numpy.arange(self.samples.size), self.samples)
        extent = numpy.absolute(self.samples).max()
        pyplot.vlines(self.onsets, -extent, extent)
        pyplot.axhline(self._threshold())
        pyplot.savefig(path)


    def _load_audio(self, path, num_samples):
        rate, samples = wavfile.read(path)
        self.rate = rate
        if num_samples:
            self.samples = samples[:num_samples].astype(numpy.int64)
        else:
            self.samples = samples.astype(numpy.int64)


    def _threshold(self):
        max_sample = self.absolute_samples.max()
        min_sample = self.absolute_samples.min()
        threshold = min_sample + (max_sample-min_sample)/6
        return threshold


    def _identify_changes(self):
        """
        identify the indices of the beginning of notes 
        (might correspond to the onset or the attack)
        using a changes in amplitude
        greater than a naive threshold
        """
        greater_mask = numpy.greater(numpy.diff(self.absolute_samples), self._threshold())
        greater_indices = [i[0] for i,j in numpy.ndenumerate(greater_mask) if j]
        self._onsets = greater_indices


    def _combine_onsets(self):
        """
        combine successive onsets that are fewer than
        ONSET_WIDTH samples apart
        """
        current = self._onsets[0]
        new_onsets = [current]
        for candidate in self._onsets[1:]:
            if candidate - current > ONSET_WIDTH:
                new_onsets.append(candidate)
                current = candidate
        self._onsets = numpy.array(new_onsets)
