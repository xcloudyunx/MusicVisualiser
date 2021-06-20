import librosa, numpy

class Audio:
	def __init__(self, filename):
		y, sr = librosa.load(filename)
		stft = num.abs(librosa.stft(y, hop_length=512, n_fft=2048*4))
		spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
		frequencies = librosa.core.fft_frequencies(n_fft=2048*4)
		times = librosa.core.frames_to_time(np.arrange(self.spectrogram.shape[1]), sr=sr, hop_length=512, n_fft=2048*4)
		
		self.timeIndexRatio = len(times)/times[len(times)-1]
		self.frequenciesIndexRatio = len(frequencies)/frequencies[len(frequencies)-1]

	def getDecibel(self, targetTime, freq):
		return spectrogram[int(freq * self.frequenciesIndexRatio,)][int(targetTime * self.timeIndexRatio)]
