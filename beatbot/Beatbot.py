import numpy 
from scipy.io import wavfile
from scipy import fftpack
from matplotlib.mlab import specgram
from matplotlib import pyplot

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
        and the most important frequencies
        """
        figure, axes = pyplot.subplots(3, sharex=True)

        axes[0].plot(numpy.arange(self.samples.size), self.samples)
        extent = numpy.absolute(self.samples).max()*1.25
        axes[0].vlines(self.onsets, -extent, extent)
        axes[0].axhline(self._threshold())

        self._identify_frequency_ranges()
        for z in range(len(self.dfts)):
            onset, dft, frequencies = self.dfts[z]
            onset_end = len(self.samples) if z == len(self.dfts)-1 else self.dfts[z+1][0]
            onset_widths = [onset_end-onset for i in range(len(frequencies))]
            axes[1].barh(frequencies, width=onset_widths, left=onset, height=5)

        axes[2].specgram(self.samples, Fs=1)
        
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


    def _identify_frequency_ranges(self, top=30, max_frequency=8000):
        """
        for each note (between two onsets),
        perform FFT
        retain only the top frequency magnitudes under the max_frequency
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
            max_frequency_index = numpy.argmax(frequencies>=max_frequency)
            dft = dft[:max_frequency_index]
            top_indices = numpy.argsort(dft)[-top:]
            top_dft = dft[top_indices]
            top_frequencies = frequencies[top_indices]
            dfts.append((onset, top_dft, top_frequencies))
        self.dfts = dfts


    def _combine_onsets(self, resolution = 2000):
        """
        combine successive onsets that are fewer than
        resolution samples apart
        """
        current = self._onsets[0]
        new_onsets = [current]
        for candidate in self._onsets[1:]:
            if candidate - current > resolution:
                new_onsets.append(candidate)
                current = candidate
        self._onsets = numpy.array(new_onsets)
