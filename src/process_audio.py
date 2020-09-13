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
        if i <= 1 or i >= len(seq) - 2:
            continue
        if seq[i - 2] < seq[i - 1] < x and seq[i + 2] < seq[i + 1] < x:
            data.append((i, x))
    return sorted(data, key=lambda x: -x[1])


def db_to_vol(db):
    transformed = 127 - 3 * abs(db)
    return transformed if transformed > 32 else 0


def keydiff(freq1, freq2):
    return abs(12 * np.log2(freq1 / freq2))


def make_note(freq, dur, vol):
    n = note.Note()
    p = pitch.Pitch()
    p.frequency = freq
    n.pitch = p
    n.duration = duration.Duration(dur)
    n.volume.velocity = vol
    return n


def make_stream(top_freqs):
    s = stream.Stream()

    freqs = np.array([f for (f, i) in top_freqs])
    intensities = np.array([i for (f, i) in top_freqs])

    print(np.shape(freqs.T))
    for voice, ints in zip(freqs.T, intensities.T):
        par = stream.Part()
        last_freq = voice[0]
        dur = 0.25
        vol = db_to_vol(ints[0])

        for note_idx in range(1, len(voice)):
            if keydiff(voice[note_idx], last_freq) >= 3:
                n = make_note(last_freq, dur, vol)
                par.append(n)

                # reset
                last_freq = voice[note_idx]
                dur = 0.25
                vol = db_to_vol(ints[note_idx])
            else:
                dur += 0.25

        n = make_note(last_freq, dur, vol)
        par.append(n)
        s.insert(0, par)
    return s  # .chordify()


ZERO_VOLUME = -80  # dB

def mute_low_volume(seq):
    return [x if x > -60 else ZERO_VOLUME for x in seq]


def make_bin2freq(sr, n_fft):
    return dict(enumerate(librosa.fft_frequencies(sr=sr, n_fft=n_fft)))


'''
return [(pitches, intensities), ... for each time step]
'''
def compute_top_frequencies(spec, n_peaks):
    bin2freq = make_bin2freq(sr=48000, n_fft=4096)
    top_freqs = []
    for time_slice in spec.T:
        pitches = []
        intensities = []

        # remove high frequencies
        # 4096: 256 = 3000 Hz, 172 = 2015 Hz
        time_slice = time_slice[:172]

        # silence murmurs
        time_slice = mute_low_volume(time_slice)

        # filter out frequencies < 70 Hz
        for i in range(6):
            time_slice[i] = ZERO_VOLUME

        # smooth the frequencies
        time_slice = savgol_filter(time_slice, 9, 3)  

        # store with intensity
        for (idx, value) in peaks(time_slice)[:n_peaks]:
            hz = bin2freq[idx]
            pitches.append(hz)
            intensities.append(value)
        pitches.sort()

        # account for not enough peaks (silence)
        while len(pitches) < n_peaks:
            pitches.append(1)
            intensities.append(ZERO_VOLUME)

        top_freqs.append((pitches, intensities))
    return top_freqs


def write_stream(path, s):
    s.insert(0, tempo.MetronomeMark(number=1500))
    s.write("midi", path)


def squash_outliers(seq):
    result = seq[:]
    for i, x in enumerate(seq):
        if i == 0 or i == len(seq) - 1:
            continue
        if seq[i - 1] == seq[i + 1]:
            result[i] = seq[i - 1]
    return result


def postprocess(top_freqs):
    # for (i, freqs_ints) in enumerate(top_freqs):
    #     if i == 0 or i == len(top_freqs) - 1:
    #         continue
    #     freqs, ints = freqs_ints
    #     for voice in range(len(freqs)):
    #         if top_freqs[i - 1][0][voice] == top_freqs[i + 1][0][voice]:
    #             top_freqs[i][0][voice] = top_freqs[i - 1][0][voice]

    freqs = np.array([f for (f, i) in top_freqs])  # timesteps x n_peaks
    by_voice = freqs.T  # n_peaks x timesteps

    for i in range(len(by_voice)):
        by_voice[i] = savgol_filter(by_voice[i], 5, 1)

    new_freqs = by_voice.T
    for i in range(len(new_freqs)):
        top_freqs[i] = (new_freqs[i], top_freqs[i][1])


def generate_midi(data, sample_rate, output_file):
    spec = librosa.stft(data.T[0], n_fft=4096, hop_length=512)
    db = librosa.amplitude_to_db(spec, ref=np.max)
    top_freqs = compute_top_frequencies(db, n_peaks=5)
    # postprocess(top_freqs)
    s = make_stream(top_freqs)
    write_stream(output_file, s)


def plot_spec(spec):
    fig, ax = plt.subplots()
    # S_dB = librosa.power_to_db(spec, ref=np.max)
    # img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sample_rate, fmax=8000, ax=ax)
    img = librosa.display.specshow(librosa.amplitude_to_db(
        spec, ref=np.max), y_axis='log', x_axis='time', ax=ax)
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
    data, sample_rate = sf.read("data/conv2.wav", dtype='float32')
    generate_midi(data, sample_rate, "conv2.mid")


if __name__ == "__main__":
    main()
