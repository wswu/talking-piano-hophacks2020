import librosa

y, sr = librosa.core.load("yuzo.wav", sr=1000)
librosa.output.write_wav("yuzo-sub.wav", y, sr)