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

def make_chord_with_velocity(freqs, intensities):
    c = chord.Chord()
    for hz, ints in zip(freqs, intensities):
        p = pitch.Pitch()
        p.frequency = hz
        n = note.Note()
        n.pitch = p
        
        n.volume.velocity = 100 - abs(ints)

        c.add(n)  # TODO: only include if it was not in the previous n chords
        c.duration = duration.Duration(0.25)
    return c

def mute_low_volume(seq):
    return [x if x > -40 else -100 for x in seq]

def compute_top_frequencies(spec, n_peaks):
    bin2freq = dict(enumerate(librosa.fft_frequencies(sr=48000, n_fft=4096)))
    top_freqs = []
    for time_slice in spec.T:
        pitches = []
        intensities = []
        time_slice = time_slice[:172]  # remove high frequencies (2048: bin 128 = 3000 Hz, bin 86 = 2015 Hz)
        # 4096: 256 = 3000 Hz, 172 = 2015 Hz
        
        # time_slice = mute_low_volume(time_slice) # causes div by zero?!

        # filter out frequencies < 70 Hz
        for i in range(6):
            time_slice[i] = -100

        time_slice = savgol_filter(time_slice, 9, 3)  # smooth the curve
        for (idx, value) in peaks(time_slice)[:n_peaks]:
            hz = bin2freq[idx]
            pitches.append(hz)
            intensities.append(value)
        pitches.sort()
        top_freqs.append((pitches, intensities))
    return top_freqs


def write(path, piece):
    s = stream.Stream()
    s.append(tempo.MetronomeMark(number=1000))
    for chord in piece:
        s.append(chord)
    s.write("midi", path)


def generate_midi(data, sample_rate):
    # spec = librosa.feature.melspectrogram(y=data.T[0], sr=sample_rate, n_fft=20000)

    spec = librosa.stft(data.T[0], n_fft=4096, hop_length=512)

    db = librosa.amplitude_to_db(spec, ref=np.max)

    top_freqs = compute_top_frequencies(db, n_peaks=5)
    
    piece = []
    for freqs, intensities in top_freqs:
        # piece.append(make_chord(freqs))
        piece.append(make_chord_with_velocity(freqs, intensities))
    write("yuzo.mid", piece)


def plot_spec(spec):
    fig, ax = plt.subplots()
    # S_dB = librosa.power_to_db(spec, ref=np.max)
    # img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sample_rate, fmax=8000, ax=ax)
    img = librosa.display.specshow(librosa.amplitude_to_db(spec, ref=np.max),y_axis='log', x_axis='time', ax=ax)
    fig.colorbar(img, ax=ax, format='%+2.0f dB')
    ax.set(title='stft')
    plt.savefig("plot.png")

def plot_db(timeslice):
    bin2freq = dict(enumerate(librosa.fft_frequencies(sr=48000, n_fft=2048)))
    plt.figure()
    plt.plot([bin2freq[b] for b in range(0, 128)], timeslice[:128])
    plt.xlabel('freq Hz')
    plt.ylabel('dB')
    plt.xscale('log')
    plt.show()
    

def main():
    data, sample_rate = sf.read("data/yuzo.wav", dtype='float32')
    generate_midi(data, sample_rate)


if __name__ == "__main__":
    main()