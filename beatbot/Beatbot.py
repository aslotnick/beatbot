import numpy 
from scipy.io import wavfile
from scipy.signal import find_peaks_cwt
from matplotlib.mlab import specgram
from matplotlib import pyplot

ONSET_WIDTH = 480

class Beatbot(object):

    def __init__(self, path):
        self._load_audio(path)
        self._onsets = []

    def _load_audio(self, path):
        rate, samples = wavfile.read(path)
        self.rate = rate
        self.samples = samples #[:20000]

    @property
    def onsets(self):
        if len(self._onsets) == 0:
            #self._identify_peaks()
            self._identify_maxes()
            self._combine_onsets()
        return self._onsets


    def _identify_maxes(self):
        """
        identify the indices of the beginning of notes 
        (might correspond to the onset or the attack)
        using a naive threshold
        """
        max_sample = numpy.abs(self.samples).max()
        threshold = max_sample/2
        greater_mask = numpy.greater(numpy.absolute(self.samples), threshold)
        greater_indices = [i[0] for i,j in numpy.ndenumerate(greater_mask) if j]
        self._onsets = greater_indices
    
    def _identify_peaks(self):
        self._onsets = find_peaks_cwt(self.samples, numpy.arange(10000, 20000))

    def _combine_onsets(self):
        current = self._onsets[0]
        new_onsets = [current]
        for candidate in self._onsets[1:]:
            if candidate - current > ONSET_WIDTH:
                new_onsets.append(candidate)
                current = candidate
        self._onsets = numpy.array(new_onsets)

       
    def plot_onsets(self, path):
        """
        save a graph of the frequency with onsets 
        """
        pyplot.plot(numpy.arange(self.samples.size), self.samples)
        extent = numpy.abs(self.samples).max()
        pyplot.vlines(self.onsets, -extent, extent)
        pyplot.savefig(path)


if __name__ == '__main__':
    b = Beatbot('shaker.wav')
    b.plot_onsets()