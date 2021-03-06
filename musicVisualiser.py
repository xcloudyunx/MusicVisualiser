import librosa, numpy, pygame, math

def clamp(minV, maxV, V):
	if V < minV:
		return minV
	if V > maxV:
		return maxV
	return V
	
def rotate(pos, angle, cor):
	angle = -math.radians(angle)
	s = math.sin(angle)
	c = math.cos(angle)
	oldX, oldY = pos
	oldX -= cor[0]
	oldY -= cor[1]
	x = c*oldX - s*oldY
	y = s*oldX + c*oldY
	x += cor[0]
	y += cor[1]
	return (x, y)

class Song:
	def __init__(self, filename):
		y, sr = librosa.load(filename)
		n_fft = 2048*4
		hop_length = 512
		stft = numpy.abs(librosa.stft(y, hop_length=hop_length, n_fft=n_fft))
		self.spectrogram = librosa.amplitude_to_db(stft, ref=numpy.max)
		frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
		times = librosa.frames_to_time(numpy.arange(self.spectrogram.shape[1]), sr=sr, hop_length=hop_length, n_fft=n_fft)
		
		self.timeIndexRatio = len(times)/times[len(times)-1]
		self.frequenciesIndexRatio = len(frequencies)/frequencies[len(frequencies)-1]
		
		pygame.mixer.music.load(filename)
		pygame.mixer.music.play(0)
		
		self.maxFrequency = frequencies[len(frequencies)-1]
		
		onsetEnv = librosa.onset.onset_strength(y, sr=sr)
		self.tempo = librosa.beat.tempo(onset_envelope=onsetEnv, sr=sr)[0]
		
		self.amplitude = numpy.mean(self.spectrogram, axis=0)											# normal trigger
		#self.amplitude = numpy.mean(self.spectrogram[0:int(100*self.frequenciesIndexRatio)], axis=0)	# bass trigger

	def getDecibel(self, targetTime, freq):
		return self.spectrogram[int(freq * self.frequenciesIndexRatio)][int(targetTime * self.timeIndexRatio)]
		
	def getMaxFrequency(self):
		return self.maxFrequency
		
	def getTempo(self):
		return self.tempo
		
	def getAmplitude(self, targetTime):
		return self.amplitude[int(targetTime * self.timeIndexRatio)]
		
class Rect:
	def __init__(self, x, y, width, height):
		self.points = [(x, y), (x, y+height), (x+width, y+height), (x+width, y)]
		
	def getPoints(self):
		return self.points
		
	def rotate(self, angle, cor):
		self.points = [rotate(pos, angle, cor) for pos in self.points]
		
class AudioBar:
	def __init__(self, freq, colour, centre, angle, minRadius=50, maxRadius=200, speed=15, width=50, minHeight=10, maxHeight=200, minDecibel=-80, maxDecibel=0):
		self.freq = freq
		self.colour = colour
		self.centre = centre
		self.width, self.height = width, minHeight
		self.minHeight, self.maxHeight = minHeight, maxHeight
		self.minDecibel, self.maxDecibel = minDecibel, maxDecibel
		
		self.decibelHeightRatio = (maxHeight-minHeight)/(maxDecibel-minDecibel)
		
		self.angle = angle
		self.speed = speed
		
		self.radius = minRadius
		self.minRadius, self.maxRadius = minRadius, maxRadius
		self.decibelRadiusRatio = (maxRadius - minRadius)/(maxDecibel-minDecibel)
		
		self.x, self.y = centre[0], centre[1]+self.radius
		
	def changeAngle(self, dt, angle):
		self.angle += dt*angle
		self.angle %= 360
		
	def changeRadius(self, dt, decibel):
		desiredRadius = decibel*self.decibelRadiusRatio + self.maxRadius
		speed = (desiredRadius - self.radius)*self.speed
		self.radius += speed * dt
		self.radius = clamp(self.minRadius, self.maxRadius, self.radius)
		
		self.y = self.centre[1]+self.radius
		
	def getFreq(self):
		return self.freq
		
	def update(self, dt, decibel):
		desiredHeight = decibel*self.decibelHeightRatio + self.maxHeight
		speed = (desiredHeight-self.height)*self.speed
		self.height += speed * dt
		self.height = clamp(self.minHeight, self.maxHeight, self.height)
		
		self.rect = Rect(self.x, self.y, self.width, self.height)
		self.rect.rotate(self.angle, self.centre)
	
	def render(self, screen):
		pygame.draw.polygon(screen, self.colour, self.rect.getPoints())
		
		
def main():
	pygame.init()
	
	s = Song(filename)
	
	infoObject = pygame.display.Info()
	screenWidth = int(infoObject.current_w/2.5)
	screenHeight = int(infoObject.current_w/2.5)
	screen = pygame.display.set_mode([screenWidth, screenHeight])

	bars = []
	frequencies = numpy.arange(0, s.getMaxFrequency()-1000, 100)
	r = len(frequencies)
	width = screenWidth/r
	angle = 0
	angleDelta = 180/r
	for i in frequencies:
		bars.append(AudioBar(i, (255, 0, 0), centre=(screenWidth/2, screenHeight/2), angle=angle, width=width))
		bars.append(AudioBar(i, (255, 0, 0), centre=(screenWidth/2, screenHeight/2), angle=360-angle, width=-width))
		angle += angleDelta
	
	t = pygame.time.get_ticks()
	getTicksLastFrame = t
	
	running = True
	while running:
		if not pygame.mixer.music.get_busy():
			running = False
	
		t = pygame.time.get_ticks()
		deltaTime = (t - getTicksLastFrame) / 1000.0
		getTicksLastFrame = t
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		
		screen.fill((50, 50, 50))
		
		amp = s.getAmplitude(pygame.mixer.music.get_pos()/1000.0)
		for b in bars:
			b.changeRadius(deltaTime, amp)
			b.changeAngle(deltaTime, s.getTempo()/10)
			b.update(deltaTime, s.getDecibel(pygame.mixer.music.get_pos()/1000.0, b.getFreq()))
			b.render(screen)
		
		pygame.display.flip()
		
	pygame.quit()
	
if __name__ == "__main__":
	main()