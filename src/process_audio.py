import librosa
import librosa.display
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from music21 import *

'''
returns sorted list of (idx, value)
'''
def peaks(seq):
    data = []
    for i, x in enumerate(seq):
        if i == 0 or i == len(seq) - 1:
            continue
        if seq[i - 1] < x and seq[i + 1] < x:
            data.append((i, x))
    return sorted(data, key=lambda x: -x[1])


def make_chord(freqs):
    c = chord.Chord()
    for hz in freqs:
        p = pitch.Pitch()
        p.frequency = hz
        n = note.Note()
        n.pitch = p
        
        n.volume.velocity = 80
        if hz > 1000:
            n.volume.velocity *= 0.8
        if hz > 2000:
            n.volume.velocity *= 0.8

        c.add(n)  # TODO: only include if it was not in the previous n chords
        c.duration = duration.Duration(0.25)
    return c


def compute_top_frequencies(spec, n_peaks):
    top_freqs = []
    for time_slice in spec.T:
        pitches = []
        time_slice = time_slice[:32]  # remove high frequencies (32 mel = 3218 Hz)
        time_slice = savgol_filter(time_slice, 7, 3)  # smooth the curve

        for (idx, value) in peaks(time_slice)[:n_peaks]:
            hz = librosa.mel_to_hz(idx)
            pitches.append(hz)
        pitches.sort()
        top_freqs.append(pitches)
    return top_freqs


def write(path, piece):
    s = stream.Stream()
    s.append(tempo.MetronomeMark(number=1000))
    for chord in piece:
        s.append(chord)
    s.write("midi", path)


def generate_midi(data, sample_rate):
    spec = librosa.feature.melspectrogram(y=data.T[0], sr=sample_rate, n_fft=20000)

    top_freqs = compute_top_frequencies(spec, n_peaks=8)
    
    piece = []
    for freqs in top_freqs:
        piece.append(make_chord(freqs))
        
    write("yuzo.mid", piece)


def plot_spec(spec):
    fig, ax = plt.subplots()
    S_dB = librosa.power_to_db(spec, ref=np.max)
    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sample_rate, fmax=8000, ax=ax)
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    ax.set(title='Mel-frequency spectrogram')
    plt.savefig("plot.png")


def main():
    data, sample_rate = sf.read("data/yuzo.wav", dtype='float32')
    generate_midi(data, sample_rate)


if __name__ == "__main__":
    main()