import pytest
from beatbot.Beatbot import Beatbot

@pytest.fixture
def metronome():
    return Beatbot('test/metronome_6.wav')

def test_metronome_onsets(metronome):
    metronome.plot_onsets('test/onsets.png')
    assert len(metronome.onsets) == 6

def test_metronome_instrument_count(metronome):
    pass

