#!/usr/local/bin/python

from tkinter import *
import random

class Dot(object):
	def __init__(self,x):
		self.r = random.randint(10,50)
		self.x = x
		self.y = 0
		self.moveSpeed = 15
		self.fallSpeed = 1
		self.colors = ['red','green','blue','purple','yellow']
		self.color = random.choice(self.colors)
		self.connections = set()

	def moveLeft(self):
		self.x -= self.moveSpeed

	def moveRight(self):
		self.x += self.moveSpeed

	def fall(self):
		self.y += self.fallSpeed

	def reverseFall(self):
		self.y -= self.fallSpeed

	def collision(self,other):
		x = self.x
		y = self.y
		x2 = other.x
		y2 = other.y
		r = self.r
		r2 = other.r
		distance = ((x-x2)**2 + (y-y2)**2)**.5
		return (distance <= r + r2)

	def connect(self,other):
		pass

	def draw(self,canvas):
		canvas.create_oval(self.x - self.r,self.y - self.r,
							self.x + self.r,self.y + self.r,fill=self.color)

		
class Dotris(object):
	def init(self):
		self.fallingDot = Dot(self.width//2)
		self.dots = []
		self.gameOver = False

	# Helper functions
	def inBounds(self,other):
		if(other.y > self.height):
			return False
		if(other.x < 0 or other.x > self.width):
			return False
		return True

	def checkCollisions(self):
		for dot in self.dots:
			if(self.fallingDot.collision(dot) == True and self.gameOver == False):
				self.dots += [self.fallingDot]
				if(self.fallingDot.y > 0):
					self.fallingDot = Dot(self.height//2)
				else:
					self.gameOver = True
				return True
		return False

	def checkGameOver(self):
		for dot in self.dots:
			if(dot.y == 1):
				self.gameOver = True

	# Events
	def mousePressed(self,event):
		pass

	def keyPressed(self,event):
		if(event.keysym == 'Left'):
			if(self.inBounds(self.fallingDot)):
				self.fallingDot.moveLeft()
		if(event.keysym == 'Right'):
			if(self.inBounds(self.fallingDot)):
				self.fallingDot.moveRight()
		if(event.keysym == 'space'):
			while(self.inBounds(self.fallingDot) == True and 
								self.checkCollisions() == False):
				self.fallingDot.fall()

		if(event.keysym == 'r'):
			print('Restarting!')
			self.init()

	def timerFired(self):

		if(self.inBounds(self.fallingDot) == True):
			self.fallingDot.fall()


		if(self.inBounds(self.fallingDot) == False and self.gameOver == False):
			self.dots += [self.fallingDot]
			self.fallingDot = Dot(self.height//2)

		# Checks for collisions
		self.checkCollisions()

		self.checkGameOver()


	def redrawAll(self):
		self.fallingDot.draw(self.canvas)
		for dot in self.dots:
			dot.draw(self.canvas)

		if(self.gameOver == True):
			print('here')
			self.canvas.create_text(self.width//2,self.height//2,
													text='Game Over',anchor='s',font='Helvetica 32')

	def run(self,width=500,height=600):
		self.root = Tk()
		self.root.title('Dotris')
		self.height = height
		self.width = width
		self.canvas = Canvas(self.root,width=self.width,
							height=self.height)
		self.canvas.pack()

		# set up events
		def redrawAllWrapper():
		    self.canvas.delete(ALL)
		    self.redrawAll()
		    self.canvas.update()


		def mousePressedWrapper(event):
		    self.mousePressed(event)
		    redrawAllWrapper()


		def keyPressedWrapper(event):
		    self.keyPressed(event)
		    redrawAllWrapper()


		self.root.bind("<Button-1>", mousePressedWrapper)
		self.root.bind("<Key>", keyPressedWrapper)

		# set up timerFired events
		self.timerFiredDelay = 10 # milliseconds
		def timerFiredWrapper():
		    self.timerFired()
		    redrawAllWrapper()
		    # pause, then call timerFired again
		    self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
		# init and get timerFired running
		self.init()
		timerFiredWrapper()
		# and launch the app
		self.root.mainloop()
		print("Closing...")


myGame = Dotris()
myGame.run()