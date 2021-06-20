import librosa, numpy, pygame

#https://medium.com/analytics-vidhya/how-to-create-a-music-visualizer-7fad401f5a69

def clamp(minV, maxV, V):
	if V < minV:
		return minV
	if V > maxV:
		return maxV
	return V

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
		
class AudioBar:
	def __init__(self, x, y, freq, colour, width=50, minHeight=10, maxHeight=100, minDecibel=-80, maxDecibel=0):
		self.x, self.y = x, y
		self.freq = freq
		self.colour = x
		self.width, self.height = width, minHeight
		self.minHeight, self.maxHeight = minHeight, maxHeight
		self.minDecibel, self.maxDecibel = minDecibel, maxDecibel
		
		self.decibelHeightRatio = (maxHeight-minHeight)/(maxDecibel-minDecibel)
		
	def update(self, dt, decibel):
		desiredHeight = decibel*self.decibelHeightRatio + self.maxHeight
		speed = (desiredHeight-self.height)/0.1
		self.height += speed * dt
		self.height = clamp(self.minHeight, self.maxHeight, self.height)
	
	def render(self, screen):
		pygame.draw.rect(screen, self.colour, (self.x, self.y+self.max_height-self.height, self.width, self.height))
		
def main():
	bars = []
	frequencies = np.arrange(100, 8000, 100)
	for i in frequencies:
		bars.append(AudioBar(x, 300, i, (255, 0, 0), max_height=400, width=w))