import pytest
from beatbot.Beatbot import Beatbot

@pytest.fixture
def metronome():
    return Beatbot('test/metronome_6.wav')

@pytest.fixture
def dual_metronome():
    return Beatbot('test/metronome_mixed_10.wav')

@pytest.fixture
def kick_hat():
    return Beatbot('test/kick_hat.wav')

def test_metronome_onsets(metronome, dual_metronome):
    assert len(metronome.onsets) == 6
    assert len(dual_metronome.onsets) == 10
    
def test_metronome_instrument_count(metronome, dual_metronome):
    metronome.plot('test/metronome.png')
    dual_metronome.plot('test/dual_metronome.png')
    dual_metronome._cluster_notes()

def test_kick_hat_onsets(kick_hat):
    kick_hat.plot('test/kick_hat.png')
    assert len(kick_hat.onsets) == 9
    kick_hat._cluster_notes()