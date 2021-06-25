import librosa, numpy, pygame, math

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
		n_fft = 2048*4
		hop_length = 512
		stft = numpy.abs(librosa.stft(y, hop_length=hop_length, n_fft=n_fft))
		self.spectrogram = librosa.amplitude_to_db(stft, ref=numpy.max)
		self.frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
		times = librosa.frames_to_time(numpy.arange(self.spectrogram.shape[1]), sr=sr, hop_length=hop_length, n_fft=n_fft)
		
		self.timeIndexRatio = len(times)/times[len(times)-1]
		self.frequenciesIndexRatio = len(self.frequencies)/self.frequencies[len(self.frequencies)-1]
		
		pygame.mixer.music.load(filename)
		pygame.mixer.music.play(0)

	def getDecibel(self, targetTime, freq):
		return self.spectrogram[int(freq * self.frequenciesIndexRatio)][int(targetTime * self.timeIndexRatio)]
		
	def getMaxFrequency(self):
		return self.frequencies[len(self.frequencies)-1]
		
class Rect:
	def __init__(self, x, y, width, height):
		self.points = [(x, y), (x, y+height), (x+width, y+height), (x+width, y)]
		
	def getPoints(self):
		return self.points
		
	def rotate(self, angle, cor):
		angle = math.radians(angle)
		s = math.sin(angle)
		c = math.cos(angle)
		for i in range(4):
			x, y = self.points[i]
			x -= cor[0]
			y -= cor[1]
			x = c*x - s*y
			y = s*x + c*y
			x += cor[0]
			y += cor[1]
			self.points[i] = (x, y)
		
class AudioBar:
	def __init__(self, x, y, freq, colour, angle, speed=10, width=50, minHeight=0, maxHeight=50, minDecibel=-80, maxDecibel=0):
		self.x, self.y = x, y
		self.freq = freq
		self.colour = colour
		self.width, self.height = width, minHeight
		self.minHeight, self.maxHeight = minHeight, maxHeight
		self.minDecibel, self.maxDecibel = minDecibel, maxDecibel
		
		self.decibelHeightRatio = (maxHeight-minHeight)/(maxDecibel-minDecibel)
		
		self.angle = angle
		self.speed = speed
		
	def getFreq(self):
		return self.freq
		
	def update(self, dt, decibel):
		desiredHeight = decibel*self.decibelHeightRatio + self.maxHeight
		speed = (desiredHeight-self.height)*self.speed
		self.height += speed * dt
		self.height = clamp(self.minHeight, self.maxHeight, self.height)
		
		self.rect = Rect(self.x, self.y, self.width, self.height)
		self.rect.rotate(self.angle, (self.x, self.y))
	
	def render(self, screen):
		#pygame.draw.rect(screen, self.colour, (self.x, self.y+self.maxHeight-self.height, self.width, self.height))
		pygame.draw.polygon(screen, self.colour, self.rect.getPoints())
		
		
def main():
	pygame.init()
	infoObject = pygame.display.Info()
	screenWidth = int(infoObject.current_w/2.5)
	screenHeight = int(infoObject.current_w/2.5)
	screen = pygame.display.set_mode([screenWidth, screenHeight])
	
	s = Song("C:/Users/Yunge/Music/Fade.wav")

	bars = []
	frequencies = numpy.arange(0, s.getMaxFrequency(), 100)
	r = len(frequencies)
	width = screenWidth/r
	x = (screenWidth - width*r)/2
	angle = 0
	angleDelta = 360/r
	for i in frequencies:
		bars.append(AudioBar(x, 300, i, (255, 0, 0), angle=angle, speed=15, maxHeight=400, width=width))
		x += width
		angle += angleDelta
	
	t = pygame.time.get_ticks()
	getTicksLastFrame = t
	
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
			b.update(deltaTime, s.getDecibel(pygame.mixer.music.get_pos()/1000.0, b.getFreq()))
			b.render(screen)
		
		pygame.display.flip()
		
	pygame.quit()
	
if __name__ == "__main__":
	main()