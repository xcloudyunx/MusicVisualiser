import librosa, numpy, pygame

#https://medium.com/analytics-vidhya/how-to-create-a-music-visualizer-7fad401f5a69

def clamp(minV, maxV, V):
	if V < minV:
		return minV
	if V > maxV:
		return maxV
	return V

class Song:
	def __init__(self, filename):
		y, sr = librosa.load(filename)
		stft = numpy.abs(librosa.stft(y, hop_length=512, n_fft=2048*4))
		self.spectrogram = librosa.amplitude_to_db(stft, ref=numpy.max)
		frequencies = librosa.core.fft_frequencies(n_fft=2048*4)
		times = librosa.core.frames_to_time(numpy.arange(self.spectrogram.shape[1]), sr=sr, hop_length=512, n_fft=2048*4)
		
		self.timeIndexRatio = len(times)/times[len(times)-1]
		self.frequenciesIndexRatio = len(frequencies)/frequencies[len(frequencies)-1]
		
		pygame.mixer.music.load(filename)
		pygame.mixer.music.play(0)

	def getDecibel(self, targetTime, freq):
		return self.spectrogram[int(freq * self.frequenciesIndexRatio,)][int(targetTime * self.timeIndexRatio)]
		
class AudioBar:
	def __init__(self, x, y, freq, colour, width=50, minHeight=10, maxHeight=100, minDecibel=-80, maxDecibel=0):
		self.x, self.y = x, y
		self.freq = freq
		self.colour = colour
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
		pygame.draw.rect(screen, self.colour, (self.x, self.y+self.maxHeight-self.height, self.width, self.height))
		
def main():
	pygame.init()
	infoObject = pygame.display.Info()
	screenWidth = int(infoObject.current_w/2.5)
	screenHeight = int(infoObject.current_w/2.5)
	screen = pygame.display.set_mode([screenWidth, screenHeight])

	bars = []
	frequencies = numpy.arange(100, 8000, 100)
	r = len(frequencies)
	width = screenWidth/r
	x = (screenWidth - width*r)/2
	for i in frequencies:
		bars.append(AudioBar(x, 300, i, (255, 0, 0), maxHeight=400, width=width))
		x += width
	
	t = pygame.time.get_ticks()
	getTicksLastFrame = t
	
	s = Song("C:/Users/Yunge/Music/Fade.wav")
	
	running = True
	while running:
		t = pygame.time.get_ticks()
		deltaTime = (t - getTicksLastFrame) / 1000.0
		getTicksLastFrame = t
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		
		screen.fill((255, 255, 255))
		
		for b in bars:
			b.update(deltaTime, s.getDecibel(pygame.mixer.music.get_pos()/1000.0, b.freq))
			b.render(screen)
		
		pygame.display.flip()
		
	pygame.quit()
	
if __name__ == "__main__":
	main()