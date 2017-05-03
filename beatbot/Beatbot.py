import numpy 
from scipy.io import wavfile
from scipy import fftpack
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
    

    def plot(self, path):
        """
        plot the samples and onsets,
        and a spectrogram
        """
        figure, axes = pyplot.subplots(4, sharex=True)

        axes[0].plot(numpy.arange(self.samples.size), self.samples)
        extent = numpy.absolute(self.samples).max()
        axes[0].vlines(self.onsets, -extent, extent)
        axes[0].axhline(self._threshold())

        #axes[1].specgram(self.samples, Fs=1)
        self._identify_frequency_ranges()
        for z in range(3):
            onset, dft, frequencies = self.dfts[z]
            axes[z+1].barh(frequencies[:10], dft[:10], left=onset)

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
        using a change in amplitude
        greater than a naive threshold
        """
        greater_mask = numpy.greater(numpy.diff(self.absolute_samples), self._threshold())
        greater_indices = [i[0] for i,j in numpy.ndenumerate(greater_mask) if j]
        self._onsets = greater_indices


    def _identify_frequency_ranges(self):
        """
        for each note (between two onsets),
        perform FFT
        retain only the top 10 frequency magnitudes
        """
        dfts = []
        num_onsets = self.onsets.size
        for o in range(num_onsets):
            onset = self.onsets[o]
            if o == num_onsets - 1:
                next_onset = None
            else:
                next_onset = self.onsets[o+1]
            note_samples = self.samples[onset:next_onset]
            dft = numpy.absolute(fftpack.rfft(note_samples))
            frequencies = fftpack.rfftfreq(note_samples.size, 1/self.rate)
            top_indices = numpy.argsort(dft)[-10:]
            top_dft = dft[top_indices]
            top_frequencies = frequencies[top_indices]
            dfts.append((onset, top_dft, top_frequencies))
        self.dfts = dfts



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
