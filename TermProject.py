from tkinter import *
from tkinter import messagebox
import speech_recognition as speech
import threading
import pyscreenshot as saveCanvas
import random
# import cv2
from PIL import Image,ImageTk,ImageOps
import PIL


################################################################################
#                               Voice Control Class
################################################################################

class VoiceThread(threading.Thread):
                # Must reset current command in the Drawing World Class 
    def __init__(self):
        super().__init__()

        # Intial variable definitions
        self.currentCommand = None
        self.currentMode = 'start'
        self.speechRecon = speech.Recognizer()
        self.auxCommand = None
        self.disabled = False
        self.kill = False  #Switch to stop thread when the program ends

        # Command lists
        self.draw_commands = ['blue','green','red','orange','purple','black',
                            'white','yellow','brown','gray','increase','grab',
                            'camera','decrease','create','draw','clear','prop',
                            'select','done','save','disable','background','help'
                            ]
        self.select_commands = ['draw','grab','erase','increase','decrease',
                                'color','outline','disable','camera','save',
                                'background','help']
        self.camera_commands = ['cheese','close','take','save','draw','prop',
                                'no','disable']
                # Added to deal very common recognition errors with 'grab'
        self.grab_misinterprets = ['grub','garage','crab']

        # Auxilary command lists (sets since order doesn't matter)
        self.help_commands = {'draw'}
        self.aux_reqCommands = {'create','increase','decrease','prop','color'}
        self.create_commands = {'circle','square','triangle'}
        self.create_auxCommands = {'circle','square','triangle'}
        self.increase_auxCommands = {'line','shape','prop'}
        self.decrease_auxCommands = {'line','shape','prop'}
        self.color_auxCommands = {'blue','red','white','orange','purple','green'
                                 ,'yellow','brown','gray'}
        self.start_commands = {'draw','help'}

        # Creates a set for the prop aux commands that come from main class
        self.prop_auxCommands = set()


    def getProps(self,propDict):
        for key in propDict:
            self.prop_auxCommands.add(key)

    # Finds auxilary commands to identify WHICH shape, increase WHAT,  etc...
    def assignAuxCommand(self,userSaid):
        #Makes our userSaid a set for easier comparison and speed
        print('\tAssigning aux command...')
        userSaid = set(userSaid)

        # If our current commands doesn't require aux commands
        if(self.currentCommand not in self.aux_reqCommands):
            userSaid = None

        # If assigns aux commands based on their respective main commands
        if(self.currentCommand == 'color'):
            userSaid = userSaid.intersection(self.color_auxCommands)
        if(self.currentCommand == 'create'):
            userSaid = userSaid.intersection(self.create_auxCommands)
        if(self.currentCommand == 'increase'):
            userSaid = userSaid.intersection(self.increase_auxCommands)
        if(self.currentCommand == 'decrease'):
            userSaid = userSaid.intersection(self.decrease_auxCommands)
        if (self.currentCommand == 'prop'):
            userSaid = userSaid.intersection(self.prop_auxCommands)

        # Pops the value resulting from the intersection, our aux command
        if(userSaid != None and userSaid != set()):
            self.auxCommand = userSaid.pop()
        #Debug Text
        print('\tAux command is: ',self.auxCommand)


    def run(self):
        while(self.disabled == False):
            # Short circuits our loop if voice thread disabled or killed
            if(self.kill == True):
                return False
            #Identifies which commands to look out for
            if (self.currentMode == 'start'):
                commands = self.start_commands
            elif(self.currentMode == 'help'):
                commands = self.help_commands
            elif (self.currentMode == 'draw'):
                commands = self.draw_commands
            elif(self.currentMode == 'select'):
                commands = self.select_commands
            elif(self.currentMode == 'camera'):
                commands = self.camera_commands

            # Speech recognition and interpretation
            with speech.Microphone() as source:
                #Debug Text
                print("\tThe current command is: ", self.currentCommand)
                print("\tI'm listening...")

                userSaid = self.speechRecon.listen(source)
                try:
                    # Get mic input and makes a list of words listened to
                    userSaid = self.speechRecon.recognize_google(userSaid)
                    userSaid = userSaid.lower()
                    userSaid = userSaid.split(' ')
                    print("\tI heard" , userSaid)
                    for word in (userSaid):
                        if(word in commands):
                            self.currentCommand = word
                            #Handles auxilary commands if needed
                            self.assignAuxCommand(userSaid)
                            # break

                        # Net captures common grab misinterpretations by API
                        if(word in self.grab_misinterprets):
                            self.currentCommand = 'grab'
                            # break

                # If speech cannot be recognized
                except speech.UnknownValueError:
                    print("I'm sorry! I couldn't understand!")
                    self.currentCommand = None

################################################################################
#                               Color Indicator Class
################################################################################


class ColorIndicator(object):
    def __init__(self,color,width):
        self.size = 50
        self.color = color
        self.xMargin = width - 10 # Avoids having our oval cut off
        self.yMargin = 10
        self.textSpacing = (2*self.size) // 4 # Divided by numnber of text lines
        self.x = self.xMargin - self.size
        self.y = self.yMargin + self.size
        self.textSize = 10
        self.hide = False

    def draw(self,canvas,color,lineThickness=1,shapeSize=100,propSize=300):
        #Prepares our text
        self.color = color
        thickStr = 'Line Width:'
        thickness = str(lineThickness)
        propSize = str(propSize)
        propSizeStr = 'Prop Size:'
        shapeSizeStr = 'Shape Size:'
        shapeSize = str(shapeSize)

        #Assures the text on the indicator will be visible
        if(self.color == 'black'):
            textColor = 'white'
        else:
            textColor = 'black'

        # Draws the circle color indicator
        canvas.create_oval(self.x - self.size,self.y - self.size,
                          self.x + self.size,self.y + self.size,fill=self.color)
        # Line Width Text
        canvas.create_text(self.x,(self.y - self.size) + self.textSpacing,
                            text=thickStr,fill=textColor,
                            font='Helvetica %d bold' % self.textSize,anchor='s')
        # Thickness
        canvas.create_text(self.x,(self.y - self.size) + (self.textSpacing),
                            text=thickness,fill=textColor,
                            font='Helvetica %d bold' % self.textSize,anchor='n')
        #Shape Size Text
        canvas.create_text(self.x,(self.y - self.size) + (2*self.textSpacing),
                            text=shapeSizeStr,fill=textColor,
                            font='Helvetica %d bold' % self.textSize,anchor='s')
        #Shape Size
        canvas.create_text(self.x,(self.y - self.size) + (2*self.textSpacing),
                            text=shapeSize,fill=textColor,
                            font='Helvetica %d bold' % self.textSize,anchor='n')
        # Prop Size Text
        canvas.create_text(self.x,(self.y - self.size) + (3*self.textSpacing),
                            text=propSizeStr,fill=textColor,
                            font='Helvetica %d bold' % self.textSize,anchor='s')
        # Prop Size
        canvas.create_text(self.x,(self.y - self.size) + (3*self.textSpacing),
                            text=propSize,fill=textColor,
                            font='Helvetica %d bold' % self.textSize,anchor='n')



################################################################################
#                               Prop Class
################################################################################

class Prop(object):
    #Prop refers to name of prop
    def __init__(self, x,y,prop,size):
        self.x = x
        self.y = y
        self.size = size
        self.selected = False
        self.rawImage = Image.open(prop)
        # Set our image created to our current size
        self.rawImageWidth,self.rawImageHeight = self.rawImage.size
        self.rawImageArea = self.rawImageHeight * self.rawImageWidth
        self.newWidth = self.size
        self.newHeight =(self.rawImageHeight//self.rawImageWidth)*self.newWidth
        self.image = self.rawImage.resize((self.newWidth,self.newHeight),
                                            resample=PIL.Image.ANTIALIAS)
        self.prop = ImageTk.PhotoImage(image=self.image)
        self.live = False

    def resize(self):
        # Resize our image
        self.newWidth = self.size
        self.newHeight =(self.rawImageHeight//self.rawImageWidth)* self.newWidth
        self.image = self.rawImage.resize((self.newWidth,self.newHeight),
                                      resample=PIL.Image.ANTIALIAS)
        self.prop = ImageTk.PhotoImage(image=self.image)

    def draw(self,canvas):
        canvas.create_image(self.x,self.y,image=self.prop)

    def drawLive(self,canvas):
        x = self.x
        y = self.y + (self.size / 2)
        canvas.create_image(x,y,image=self.prop)


    def containsPoint(self,x,y):
        halfSize = self.size / 2
        xLBound = self.x - halfSize
        xRBound = self.x + halfSize
        yDownBound = self.y - halfSize
        yUpBound = self.y + halfSize
        if(x > xLBound and x < xRBound and y > yDownBound and y < yUpBound):
            return True
        else:
            return False

    def move(self,point):
        x,y = point
        self.x = x
        self.y = y

    def multiMove(self,shiftHorizontal,shitfVertical):
        self.x = self.x + shiftHorizontal
        self.y = self.y + shitfVertical

    def highlight(self,canvas):
        halfSize = self.size / 2
        canvas.create_image(self.x,self.y,image=self.prop)
        canvas.create_rectangle(self.x - (self.size / 2),self.y - halfSize,
                                self.x + (self.size / 2),self.y + halfSize)


        
################################################################################
#                               Shape Classes
################################################################################

class Shape(object):

    def __init__(self,x,y,color,size,outline):
        self.x = x
        if(size > 5):
            self.size = size
        else:
            self.size = 5
        self.selected = False
        self.y = y
        self.color = color
        self.outline = outline

    def containsPoint(self,x,y):
        xLBound = self.x - self.size
        xRBound = self.x + self.size
        yDownBound = self.y - self.size
        yUpBound = self.y + self.size
        if( x > xLBound and x < xRBound and y < yUpBound and y > yDownBound):
            return True
        return False

    def move(self,point):
        x,y = point
        self.x = x
        self.y = y

    def multiMove(self,shiftHorizontal,shitfVertical):
        self.x = self.x + shiftHorizontal
        self.y = self.y + shitfVertical

###########################################
# Circle Subclass
###########################################
    
class Circle(Shape):

    def __init__(self, x,y,color,size,outline='black'):
        super().__init__(x,y,color,size,outline)

    def draw(self,canvas):
        canvas.create_oval(self.x - self.size,self.y - self.size,
                           self.x + self.size,self.y + self.size,
                           fill=self.color,outline=self.outline)

    def highlight(self,canvas):
        canvas.create_oval(self.x - self.size,self.y - self.size,
                           self.x + self.size,self.y + self.size,
                           fill=self.color,outline='cyan')

###########################################
# Square Subclass
###########################################

class Square(Shape):
    def __init__(self, x,y,color,size,outline='black'):
        super().__init__(x,y,color,size,outline)

    def draw(self,canvas):
        canvas.create_rectangle(self.x - self.size,self.y - self.size,
                           self.x + self.size,self.y + self.size,
                           fill=self.color,outline=self.outline)

    def highlight(self,canvas):
        canvas.create_rectangle(self.x - self.size,self.y - self.size,
                           self.x + self.size,self.y + self.size,
                           fill=self.color,outline='cyan')

###########################################
# Triangle Subclass
###########################################


class Triangle(Shape):
    def __init__(self, x,y,color,size,outline='black'):
        super().__init__(x,y,color,size,outline)

    def draw(self,canvas):
        canvas.create_polygon(self.x - self.size,self.y + self.size,
                              self.x + self.size,self.y + self.size,
                              self.x ,self.y - self.size,
                           fill=self.color,outline=self.outline)

    def highlight(self,canvas):
        canvas.create_polygon(self.x - self.size,self.y + self.size,
                              self.x + self.size,self.y + self.size,
                              self.x ,self.y - self.size,
                           fill=self.color,outline='cyan')


################################################################################
#                               Drawing Object Class
################################################################################

class DrawingObject(object):
    def __init__(self,color,points,size=1):
        self.color = color
        self.points = points
        self.selected = False
        self.size = size
        self.referencePoint = None
        self.thickfillDivisor = 2.4

    def draw(self,canvas):
        if(len(self.points) > 1):
            for point in range(len(self.points) - 2):
                canvas.create_line(self.points[point],
                                   self.points[point + 1],
                                    fill=self.color,width=self.size)
                if(self.size > 5):
                    x,y = self.points[point]
        # Makes the circle at points when thickness is large to avoid 'slicing'
                    thickerFill = self.size / self.thickfillDivisor
                    canvas.create_oval(x - thickerFill, y - thickerFill,
                                       x + thickerFill,y + thickerFill,
                                       fill=self.color,outline=self.color)

    def isBetween(self,value,bound1,bound2):
        leftBound = min(bound1,bound2)
        rightBound = max(bound1,bound2)
        if(value > leftBound and value < rightBound):
            return True
        else:
            return False

    def containsPoint(self,x,y):
        for point in self.points:
            pointx,pointy, = point
            for point2 in self.points:
                point2x,point2y = point2
                if(self.isBetween(x,pointx,point2x) == True):
                    if(self.isBetween(y,pointy,point2y) == True):
                        return True
        return False

    def move(self,point):
        x,y = point
        x2,y2 = self.points[len(self.points)//2]
        horizontalShift = x - x2
        verticalShift = y - y2
        for point in range(len(self.points)):
            prevPointX,prevPointY = self.points[point]
            newPoint = (prevPointX + horizontalShift,prevPointY + verticalShift)
            self.points[point] = newPoint

    def multiMove(self,shiftHorizontal,shitfVertical):
        for point in range(len(self.points)):
            prevPointX,prevPointY = self.points[point]
            newPoint = (prevPointX + shiftHorizontal,prevPointY + shitfVertical)
            self.points[point] = newPoint


    # Draw function except colors it cyan to indicate its been selected
    def highlight(self,canvas):
        if(len(self.points) > 1):
            for point in range(len(self.points) - 2):
                canvas.create_line(self.points[point],
                                   self.points[point + 1],
                                    fill='cyan',width=self.size)
                if(self.size > 5):
                    x,y = self.points[point]
        # Makes the circle at points when thickness is large to avoid 'slicing'
                    thickerFill = self.size / self.thickfillDivisor
                    canvas.create_oval(x - thickerFill, y - thickerFill,
                                       x + thickerFill,y + thickerFill,
                                       fill='cyan',outline='cyan')


################################################################################
#                               Main Program Class
################################################################################


class DrawingWorld(object):

################################################################################
#                             Initializer Functions
################################################################################

     # Initializes our help screen and saves their references
    def getHelpScreens(self):
        # Opens both help screen images and prepares new sizes
        rawImage = Image.open('help1.gif')
        rawImage2 = Image.open('help2.gif')
        toolbarOffset = 15 # Used to avoid the bottom of the image being cut
        width = self.width
        height = self.height - toolbarOffset

        # Resizes the images
        helpScreen1 = rawImage.resize((width,height),Image.ANTIALIAS)
        helpScreen2 = rawImage2.resize((width,height),Image.ANTIALIAS)

        # References and adds to class attributes
        self.helpScreen1 = ImageTk.PhotoImage(helpScreen1)
        self.helpScreen2 = ImageTk.PhotoImage(helpScreen2)

        #Sets up our props from our proplist.txt file
    def setUpProps(self):
        self.propDict = {}
        propListFile = open('proplist.txt','r')
        for line in propListFile:
            #Used to elimate '\n' and the '.gif' from our list
            lineKey = line[:len(line) - 5:]
            fileName = line[:len(line) - 1]
            self.propDict[lineKey] = fileName

        # Initilizes the voice thread for voice controls and feeds it the props
    def initializeVoiceThread(self):
        self.voiceThread = VoiceThread()
        self.props = self.voiceThread.getProps(self.propDict)
        self.voiceThread.start()

    def startFaceDetector(self):
        preTrainedDetector = 'haarcascade_frontalface_default.xml'
        self.faceDetection = cv2.CascadeClassifier(preTrainedDetector)

################################################################################
#                                       Init
################################################################################

    def init(self):
        # Default strings
        self.currentMode = 'start'
        self.currentColor = 'black'
        self.cursorimg = 'pencil'

        # Default toggles
        self.draw = False
        self.grab = False
        self.select = False
        self.create_shape = False
        self.import_prop = False
        self.capture = False
        self.liveProp = False
        self.backgroundSet = False

        # Features not yet launched or created
        self.currentShape = None
        self.selectedDrawing = None
        self.currentProp = None
        self.camera = None
        self.currentFrame = None
        self.faceDetectionFrame = None
        self.background = None

        # Default number values
        self.defaultLineThickness = 1 # Stored in order to keep as smallest val
        self.thickness = 1 # Refers to line
        self.thickfillDivisor = 2.4 # Fixes slicing glitch in drawn objects
        self.shapeSize = 50
        self.propSize = 300
        self.thickIncrease = 5
        self.shapeIncrease = 25
        self.propIncrease = 50
        self.livePropSize = 375
        self.helpScreen = 1 # Help screen that will be currently showing
        self.drawings = 0 # Total saved drawings

        # Lists for interface options
        self.colors = {'blue','green','red','orange','purple','black','white',
                      'yellow','brown','gray'}
        self.debug_colors = {'1':'red','2': 'orange','3':'yellow','4':'green',
                            '5':'blue','6':'purple','7':'brown','8':'white',
                            '9':'gray','0':'black'}
        self.debug_create_shapes = {'comma':'triangle','period':'square',
                                    'slash':'circle'}
        self.select_drawings = {}

        self.cursors = {'draw':'pencil','triangle':'tcross','circle':'circle',
                        'square':'box_spiral'}

        # Loads initial objects and object holders
        self.colorIndicator = ColorIndicator('black',self.width)
        self.currentPoints = list()
        self.drawingObjects = list()
        self.liveProps = list()

        # Calls initializer functions
        self.getHelpScreens()
        self.setUpProps() 
        self.initializeVoiceThread()
        self.startFaceDetector()

################################################################################
#                               Helper Functions
################################################################################'

    def voiceControlToggle(self):
        if(self.voiceThread.disabled == False):
            self.voiceThread.disabled = True
            messagebox.showinfo('Voice Commands',
                                'Voice commands have been disabled')
        else:
            messagebox.showinfo('Voice Commands',
                                'Voice commands have been enabled')
            self.initializeVoiceThread()

    def inWindow(self,event): # Window refers on the canvas, not the topbar
        if(event.x > 0 and event.y > 0 and event.x < self.width 
                                        and event.y < self.height):
            return True
        else:
            return False

    def showHelp(self):
        self.currentMode = 'help'
        self.voiceThread.currentMode = 'help'

    def setDrawMode(self):
            self.liveProps = []
            self.grab = False
            self.cursorimg = 'pencil'
            self.import_prop = False
            for key in self.select_drawings:
                self.select_drawings[key].selected = False
            self.currentMode = 'draw'
            self.voiceThread.auxCommand = None
            self.liveProp = False
            self.voiceThread.auxCommand = None

    def enableSelectMode(self):
        self.select = True
        self.grab = False
        self.currentMode = 'select'
        self.cursorimg = 'plus'

    # Changes color for selection and in general
    def changeColor(self):
        newColor = self.voiceThread.auxCommand
        for key in self.select_drawings:
            self.select_drawings[key].color = newColor
        self.voiceThread.currentCommand = 'select'


    def startGrab(self):
        # Avoid spawning objects on grab click
        if(self.grab == False):
            self.grab = True
            self.create_shape = False
            self.draw = False
            self.import_prop = False
            self.cursorimg = 'openhand'
            self.voiceThread.currentCommand = 'None'

    def SingleGrab(self,event):
        for drawing in self.drawingObjects:
            if(drawing.containsPoint(event.x,event.y) == True):
                self.selectedDrawing = drawing
                #If drawing is grabbed, changes the cursor
                self.cursorimg = 'closedhand'

    def grabMove(self,event):
        self.selectedDrawing.move((event.x,event.y))
        self.cursorimg = 'closedhand'

    def grabRelease(self,event):
        self.grabMove(event)
        self.cursorimg = 'openhand'
        self.selectedDrawing = None
        self.voiceThread.currentCommand = 'None'

        # Sets up variabl to create shapes
    def shapeInitializer(self):
        self.create_shape = True
        self.import_prop = False
        self.draw = False
        self.grab = False
        self.currentShape = self.voiceThread.auxCommand
        self.cursorimg = self.cursors[self.currentShape]

    def shapeCreator(self,event):
        if(self.currentShape == 'circle'):
            self.drawingObjects += [Circle(event.x,event.y,
                                    self.currentColor,self.shapeSize)]
        if(self.currentShape == 'square'):
            self.drawingObjects += [Square(event.x,event.y,
                                    self.currentColor,self.shapeSize)]
        if(self.currentShape == 'triangle'):
            self.drawingObjects += [Triangle(event.x,event.y,
                                    self.currentColor,self.shapeSize)]

        #Sets up variables to create props
    def propInitializer(self):
        self.import_prop = True
        self.create_shape = False
        self.draw = False
        self.grab = False
        self.cursorimg='pointinghand'
        try:
            self.currentProp=self.propDict[self.voiceThread.auxCommand]
        except:
            print('Command does not exist')


        #Imports a prop
    def importProp(self,event):
        self.drawingObjects += [Prop(event.x,event.y,self.currentProp,
                                self.propSize)]

    def increaseSize(self):
        #In the case of shapes
        if(self.voiceThread.auxCommand == 'shape'):
            self.shapeSize += self.shapeIncrease
        #In the case of a prop
        if(self.voiceThread.auxCommand == 'prop'):
            self.propSize += self.propIncrease
        #In the case of line thickness
        if(self.voiceThread.auxCommand == 'line'):
        # Makes our thickness increase by a easy number like 5
            if(self.thickness == 1):
                self.thickness = self.thickIncrease
            else:
                self.thickness += self.thickIncrease
        self.voiceThread.currentCommand = None

    def decreaseSize(self):
        #In the case of shapes
        if(self.voiceThread.auxCommand == 'shape'):
            self.shapeSize -= self.shapeIncrease
        #In the case of a prop
        if(self.voiceThread.auxCommand == 'prop'):
            self.propSize -= self.propIncrease
        #In the case of line thickness
        if(self.voiceThread.auxCommand == 'line'):
        # Makes our thickness increase by a easy number like 5
            if(self.thickness > 5):
                self.thickness -= self.thickIncrease
            else:
                self.thickness = self.defaultLineThickness
        self.voiceThread.currentCommand = None


    # Increases sisze of selection by one respective size interval of their type
    def multiIncreaseSize(self):
        for key in self.select_drawings:
            # If Shape uses shape interval
            if(isinstance(self.select_drawings[key],Shape) == True):
                self.select_drawings[key].size += self.shapeIncrease
            # If Prop uses prop interval
            if(isinstance(self.select_drawings[key],Prop) == True):
                self.select_drawings[key].size += self.propIncrease
                self.select_drawings[key].resize()
            # If line uses line interval
            if(isinstance(self.select_drawings[key],DrawingObject) == True):
                if(self.select_drawings[key].size == 1):
                    self.select_drawings[key].size = 5
                else:
                    self.select_drawings[key].size += self.thickIncrease
        self.voiceThread.currentCommand = 'None'

    def multiDecreaseSize(self):
        for key in self.select_drawings:
            # If Shape uses shape interval
            if(isinstance(self.select_drawings[key],Shape) == True):
                self.select_drawings[key].size += self.shapeIncrease
            # If Prop uses prop interval
            if(isinstance(self.select_drawings[key],Prop) == True):
                self.select_drawings[key].size += self.propIncrease
                self.select_drawings[key].resize()
            # If line uses line interval
            if(isinstance(self.select_drawings[key],DrawingObject) == True):
                if(self.select_drawings[key].size == 1):
                    self.select_drawings[key].size = 5
                else:
                    self.select_drawings[key].size += self.thickIncrease
        self.voiceThread.currentCommand = 'None'

        # Function used to select all items and de-select them
    def multiSelect(self,event):
        for drawing in self.drawingObjects:
            index = self.drawingObjects.index(drawing)
            if(drawing.containsPoint(event.x,event.y)):
                if(drawing.selected == False):
                    self.select_drawings[index] = drawing
                    drawing.selected = True
                else: # In order to de-select
                    del self.select_drawings[index]
                    drawing.selected = False

    #Manages moving a group of objects as opposed to the simpler one
    def multiGrab(self,event):
        # Sets up reference points and finds vertical and horizontal shifts
        refx,refy = self.select_referencePoint
        hShift = event.x - refx
        vShift = event.y - refy
        self.cursorimg = 'closedhand'
        for key in self.select_drawings:
            self.select_drawings[key].multiMove(hShift,vShift)
        self.select_referencePoint = (event.x,event.y)

     #Toggles the outline on and off
    def toggleOutline(self):
        for key in self.select_drawings:
            currentShape = self.select_drawings[key]
            if(isinstance(currentShape,Shape) == True):
                if(currentShape.outline == 'black'):
                    currentShape.outline = currentShape.color
                else:
                    currentShape.outline = 'black'

    #Erases all items selected
    def eraseSelection(self):
        for key in self.select_drawings:
                self.drawingObjects[key] = None

    def launchCamera(self):
        self.currentMode = 'camera'
        self.voiceThread.currentMode = 'camera'

        #Set up dimensions for capture as well as camera
        self.camera = cv2.VideoCapture(0) 
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,self.height)
        self.capture = True
        self.liveProps = [] #Resets live props

    def toggleLiveProp(self):
        if(self.liveProp == False):
            self.capture = True
            self.liveProp = True
            self.voiceThread.currentCommand = 'prop'
            self.voiceThread.auxCommand = 'kanye'
        else:
            self.liveProp = False
            self.capture = True
            self.liveProps = []
            self.voiceThread.currentCommand = 'None'


    def previewPicture(self):
        self.capture = False #Stop camera on the last frame


    def retakePicture(self):
        self.capture = True #Unblocks the camera and resets voice thread
        self.voiceThread.currentCommand = 'None'

        # Activates and identifies the live prop
    def activateLiveProp(self):
        self.currentProp = self.voiceThread.auxCommand
        # You cant wear a dress on your head
        if(self.voiceThread.auxCommand == 'dress'):
            self.currentProp = 'bernie'
        self.liveProp = True
        self.voiceThread.currentCommand = None 

    def setCanvasBackground(self):
       if(self.capture == False): # Assures that the camera has been paused
            self.background = self.currentFrame
            self.drawingObjects = []
            self.drawingObjects += self.liveProps
            self.backgroundSet = True
            self.voiceThread.currentCommand = None
            self.currentMode = 'draw'
            self.liveProp = False

    def removeBackground(self):
        self.background = None
        self.backgroundSet = False

    def captureFromWebcam(self):
        retrn,frame = self.camera.read() 
        self.frame = cv2.flip(frame,1)

        # Has exception to processing unecessary images
        if(self.liveProp == True):
            try: # Prevents camera from crashing
                self.analyzeFaces()
            except:
                pass

        #Displays our frame as tk image
        cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
        self.currentFrame = Image.fromarray(cv2image)
        self.currentFrame = ImageTk.PhotoImage(image=self.currentFrame)

            

    def analyzeFaces(self):
        hairoffset = 20 # Used to avoid hair on kanye and keep trump's flow
        self.currentProp = self.propDict[self.voiceThread.auxCommand]
        self.liveProps = [] #Refreshes the live Props per frame

        # Makes new grey image to analyze for faces
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self.faceDetection.detectMultiScale(self.gray,1.3,3)
        for (x,y,w,h) in faces:
            y = y - hairoffset
            x = x + (self.livePropSize / 2)

        # Creates new props with face frame coordinates
        self.liveProps += [Prop(x,y,self.currentProp,self.livePropSize)]

    def saveDrawingToDisk(self):
        # First hides the color indicator
        if(self.colorIndicator.hide == False):
            self.colorIndicator.hide = True
        else:
        # Takes a screen shot of our canvas and saves it to the disk
            menuBarMargin = 20
            windowBarMargin = 25
            totalMargin = menuBarMargin + windowBarMargin
            canvasImage =saveCanvas.grab(bbox=(0,totalMargin,self.width,
                                                self.height))
            canvasImage.save('My Drawing%d.png' % self.drawings) 
            message = "Drawing Saved"
            title = "Status"
            messagebox.showinfo(title, message)
            #Unhides the indicator
            self.colorIndicator.hide = False
            self.voiceThread.currentCommand = None

    def drawColorIndicator(self):
        self.colorIndicator.draw(self.canvas,self.currentColor,
                                self.thickness,self.shapeSize,self.propSize)


    def clear(self):
        self.drawingObjects = list()
        self.liveProps = list()
        self.voiceThread.currentCommand = False


################################################################################
#                               Main Event Functions
################################################################################'

    def mouseReleased(self,event):
        if(self.currentMode == 'draw'):
            self.drawMouseReleased(event)
        if(self.currentMode == 'select'):
            self.selectMouseReleased(event)



    def mouseMoved(self,event):
        if(self.inWindow(event) == True):
            if(self.currentMode == 'draw'):
                self.drawMouseMoved(event)
            elif(self.currentMode == 'select'):
                self.selectMouseMoved(event)

    def mousePressed(self,event): 
        if(self.inWindow(event) == True):
            if(self.currentMode == 'start'):
                self.startMousePressed(event)
            elif(self.currentMode == 'help'):
                self.helpMousePressed(event)
            elif(self.currentMode == 'draw'):
                self.drawMousePressed(event)
            elif(self.currentMode == 'select'):
                self.selectMousePressed(event)

    def keyPressed(self,event):
        # Voice control toggle
        if(event.keysym == 'v'):
            self.voiceControlToggle()
        if(event.keysym == 'h'):
            self.voiceThread.currentCommand = 'help'
        elif(self.currentMode == 'start'):
            self.startKeyPressed(event)
        elif(self.currentMode == 'help'):
            self.helpKeyPressed(event)
        elif(self.currentMode == 'draw'):
            self.drawKeyPressed(event)
        elif(self.currentMode == 'select'):
            self.selectKeyPressed(event)
        elif(self.currentMode == 'camera'):
            self.cameraKeyPressed(event)


    def timerFired(self):
        if(self.voiceThread.currentCommand == 'help'):
            self.currentMode = 'help' 
        if(self.voiceThread.currentCommand == 'disable'):
            self.voiceThread.disabled = True
        if(self.currentMode == 'start'):
            self.startTimerFired()
        elif(self.currentMode == 'help'):
            self.helpTimerFired()
        elif(self.currentMode == 'draw'):
            self.drawTimerFired()
        elif(self.currentMode == 'select'):
            self.selectTimerFired()
        elif(self.currentMode == 'camera'):
            self.cameraTimerFired()

    def redrawAll(self):
        if(self.currentMode == 'start'):
            self.startRedrawAll()
        elif(self.currentMode == 'help'):
            self.helpRedrawAll()
        elif(self.currentMode == 'draw' or self.currentMode == 'select'):
            self.drawRedrawAll()
        elif(self.currentMode == 'camera'):
            self.cameraRedrawAll()


################################################################################
#                               Camera Mode
################################################################################


    def cameraKeyPressed(self,event):
    # Debug Buttons
        if(event.keysym == 'd'):
            self.voiceThread.currentCommand = 'draw'

        if(event.keysym =='c'):
            self.voiceThread.currentCommand = 'cheese'
        if(event.keysym == 's'):
            self.voiceThread.currentCommand = 'save'
        if(event.keysym == 't'):
            self.voiceThread.currentCommand = 'take'
        if(event.keysym == 'p'):
            self.toggleLiveProp()


    def cameraTimerFired(self):

        # Sets voice thread to camera mode
        self.voiceThread.currentMode = 'camera'

        if(self.voiceThread.currentCommand == 'cheese'):
            self.previewPicture()

        elif(self.voiceThread.currentCommand == 'take'):
            self.retakePicture()

        elif(self.voiceThread.currentCommand == 'prop'):
            self.activateLiveProp()

        elif(self.voiceThread.currentCommand == 'save'):
            self.setCanvasBackground()


        elif(self.voiceThread.currentCommand == 'draw'):
            self.setDrawMode()

        if(self.capture == True):
            self.captureFromWebcam()
            

    def cameraRedrawAll(self):
        # Draws our current frame
        self.midpoint = self.width/2
        self.canvas.create_image(self.midpoint,0,image=self.currentFrame,
                                                                anchor='n')
        # Draws our props if enabled
        for prop in self.liveProps:
            prop.drawLive(self.canvas)




################################################################################
#                               Select Mode
################################################################################

    def selectMousePressed(self,event):
        if(self.grab == False):  
            self.multiSelect(event)
        if(self.grab == True):
            #Sets reference point to examine drag
            self.cursorimg = 'closedhand'
            self.select_referencePoint = (event.x,event.y)

    def selectMouseMoved(self,event):
        if(self.grab == True):
            self.multiGrab(event)

    def selectMouseReleased(self,event):
        if(self.grab == True):
            self.enableSelectMode()
            

    def selectKeyPressed(self,event):
        if(event.keysym in self.debug_colors):
            self.voiceThread.currentCommand = 'color'
            self.voiceThread.auxCommand = self.debug_colors[event.keysym]
        if(event.keysym == 'i'):
            self.voiceThread.currentCommand = 'increase'
        if(event.keysym == 'g'):
            self.voiceThread.currentCommand = 'grab'
        if(event.keysym == 'd'):
            self.voiceThread.currentCommand = 'draw'
        if(event.keysym == 'e'):
            self.voiceThread.currentCommand = 'erase'
        if(event.keysym == 'u'):
            self.voiceThread.currentCommand = 'outline'
        if(event.keysym == 'c'):
            self.voiceThread.currentCommand = 'camera'


    def selectTimerFired(self):
        # Sets voice thread to select mode
        self.voiceThread.currentMode = 'select'

        # Returns us to the drawing mode
        if(self.voiceThread.currentCommand == 'draw'):
            self.setDrawMode()

        if(self.voiceThread.currentCommand == 'camera'):
            self.launchCamera()

        if(self.voiceThread.currentCommand == 'save'):
            self.saveDrawingToDisk()

        # Toggles the outline on and off
        if(self.voiceThread.currentCommand == 'outline'):
            self.toggleOutline()

        # Enables multi grab
        if(self.voiceThread.currentCommand == 'grab'):
            self.startGrab()

        # If the color is changed for the selection
        if(self.voiceThread.currentCommand == 'color'):
            self.changeColor()

         #Erases all items selected
        if(self.voiceThread.currentCommand == 'erase'):
            self.eraseSelection()

        # Size is increased for the selection
        if(self.voiceThread.currentCommand == 'increase'):
            self.multiIncreaseSize()

        if(self.voiceThread.currentCommand == 'decrease'):
            self.multiDecreaseSize()

        if(self.voiceThread.currentCommand == 'clear'):
            self.clear()

        





################################################################################
#                               Draw Mode
################################################################################
    
    def drawMousePressed(self,event):
        # In case the user is wants to grab an object
        if(self.grab == True):
            self.SingleGrab(event)

         # Adds the shape to the object list when creating object           
        elif(self.create_shape == True):
            self.shapeCreator(event)

        elif(self.import_prop == True):
            self.importProp(event)
        else:
            # Keeps track of the initial click, the origin of the line
            self.draw = True

        # In both cases must record the current points of the click
        self.currentPoints = [(event.x,event.y)]


    def drawMouseMoved(self,event):
        if(self.draw == True):
            self.currentPoints += [(event.x,event.y)]

        #Keeps track of our curring drawing
        if(self.grab == True and self.selectedDrawing != None):
            self.grabMove(event)
            self.cursorimg = 'closedhand'
            
    def drawMouseReleased(self,event):
        if(self.grab == True and self.selectedDrawing != None):
            self.grabRelease(event)

        elif(self.draw == True):
            # Finishes the drawing and makes it an object
            self.draw = False
            self.drawingObjects += [DrawingObject(self.currentColor,
                                    self.currentPoints,self.thickness)]

    def drawTimerFired(self):

        # Sets voice thread to draw mode
        self.voiceThread.currentMode = 'draw'

        # Makes sure our camera turns off when returning to drawing mode
        if(self.camera != None):
            if(self.camera.isOpened()):
                self.camera.release()

        # Enables the camera mode
        if(self.voiceThread.currentCommand == 'camera'):
            self.launchCamera()

        # Keeps track of the color we are using
        elif(self.voiceThread.currentCommand in self.colors):
            self.currentColor = self.voiceThread.currentCommand

        # Enables select
        elif(self.voiceThread.currentCommand == 'select'):
            self.enableSelectMode()

        # Enables grab
        elif(self.voiceThread.currentCommand == 'grab'):
            self.startGrab()
            
        # Initializes shape creation variables
        elif(self.voiceThread.currentCommand == 'create'):
            self.shapeInitializer()

        # Enables the import of props
        elif(self.voiceThread.currentCommand == 'prop'):
            self.propInitializer()

        # Reset command to keep drawing
        elif(self.voiceThread.currentCommand == 'draw'):
            self.setDrawMode()

        # Deletes everything on the canvas
        elif(self.voiceThread.currentCommand == 'clear'):
            self.clear()


        # Handles size and thickness increases
        elif(self.voiceThread.currentCommand == 'increase'):
            self.increaseSize()

        # Handles size and thickness decreases
        elif(self.voiceThread.currentCommand == 'decrease'):
            self.decreaseSize()

        if(self.voiceThread.currentCommand == 'save'):
            self.saveDrawingToDisk()


    def drawKeyPressed(self,event):
        # Debug buttons
        if(event.keysym in self.debug_colors):
            self.voiceThread.currentCommand = self.debug_colors[event.keysym]
        if(event.keysym in self.debug_create_shapes):
            self.voiceThread.currentCommand = 'create'
            self.voiceThread.auxCommand = self.debug_create_shapes[event.keysym]
        if(event.keysym == 'p'):
            self.voiceThread.currentCommand = 'prop'
            self.voiceThread.auxCommand = 'kanye'
        if(event.keysym == 'g'):
            self.voiceThread.currentCommand = 'grab'
        if(event.keysym == 'equal'):
            self.voiceThread.currentCommand = 'increase'
            self.voiceThread.auxCommand = 'line'
        if(event.keysym == 'minus'):
            self.voiceThread.currentCommand = 'decrease'
            self.voiceThread.auxCommand = 'line'
        if(event.keysym == 'd'):
            self.voiceThread.currentCommand = 'draw'
        if(event.keysym == 'e'):
            self.voiceThread.currentCommand = 'clear'
        if(event.keysym == 's'):
            self.voiceThread.currentCommand = 'select'
        if(event.keysym == 'S'):
            self.voiceThread.currentCommand = 'save'
        if(event.keysym == 'c'):
            self.voiceThread.currentCommand = 'camera'


    def drawRedrawAll(self):

        #Triggers if we took a picture for our background
        if(self.backgroundSet == True):
            self.canvas.create_image(self.midpoint,0,image=self.background,
                                    anchor='n')

        # Draws the finished object in sync with the deleting of current drawing
        for drawing in (self.drawingObjects):
            if(drawing != None):
                index = self.drawingObjects.index(drawing)
            if(self.selectedDrawing == drawing):
                drawing.highlight(self.canvas)
            if(index in self.select_drawings and drawing.selected == True):
                drawing.highlight(self.canvas)
            else:
                if(drawing in self.liveProps):
                    drawing.drawLive(self.canvas)
                else:
                    drawing.draw(self.canvas)

        # Must display indicator on top, unless saving canvas
        if(self.colorIndicator.hide == False):
            self.drawColorIndicator()

        # Displays the line as we draw it and then gets deleted
        if(len(self.currentPoints) > 1 and self.draw== True):
            for point in range(len(self.currentPoints) - 2):
                self.canvas.create_line(self.currentPoints[point],
                                        self.currentPoints[point + 1],
                                        fill=self.currentColor,
                                        width=self.thickness)

        # Makes circle to cover 'slicing' glitch
                if(self.thickness > 5):
                    x,y = self.currentPoints[point]
                    thickerFill = self.thickness / self.thickfillDivisor
                    self.canvas.create_oval(x - thickerFill, y - thickerFill,
                                       x + thickerFill,y + thickerFill,
                                       fill=self.currentColor,
                                       outline=self.currentColor)


################################################################################
#                               Start Mode
################################################################################
    
    def startMouseMoved(self,event):
        pass

    def startMousePressed(self,event):
        pass

    def startKeyPressed(self,event):
        if(event.keysym == 'd'):
            self.voiceThread.currentCommand = 'draw'
        if(event.keysym == 'h'):
            self.voiceThread.currentCommand = 'help'

    def startTimerFired(self):
        if(self.voiceThread.currentCommand in self.voiceThread.start_commands):
            self.currentMode = self.voiceThread.currentCommand
            self.voiceThread.currentMode = self.currentMode

    def startRedrawAll(self):
        

    #############################
    # Title Sequence
    #############################
        colorString = 'Welcome to Drawing World'
        margin = self.width // 8
        colors = ['red','blue','green','yellow','orange','purple']
        marker = 0
        titleLetterSize = 30
        titleBorderSize = titleLetterSize + 2 
        titleHeight = self.height / 2 # Reference for other text
        letterSpacing = (self.width - (2 * margin)) // len(colorString)
        # Makes all the title different colors
        for letter in colorString:
            # Creates a copy of the letter in black to give it an outline
            self.canvas.create_text(margin + marker, titleHeight,
                                    text=letter,fill='black',
                                    font='Helvetica %d bold' % titleBorderSize,
                                    anchor='s')
            self.canvas.create_text(margin + marker, titleHeight,
                                    text=letter,
                                    fill=random.choice(colors),
                                    font='Helvetica %d underline' 
                                    % titleLetterSize,
                                    anchor='s')
            marker += letterSpacing
        subtitleSize = titleLetterSize // 1.3
        subtitleBorderSize = subtitleSize + 2

    #############################
    # Help Option
    #############################
        #Variable to center all subtitles
        textCenter = margin + ((self.width - (2 * margin)) // 2)
        titleSpacing = titleHeight / 5 #Refers to vertical spacing
        helpTitleHeight = titleSpacing + titleHeight
        self.canvas.create_text(textCenter,helpTitleHeight,
                        text='Say "help" at any moment to show the help screen',
                                fill='red',
                                font='Helvetica %d bold' % subtitleSize,
                                anchor='s')
    #############################
    # Draw Option
    #############################
        titleSpacing = titleHeight / 5
        drawTitleHeight = titleSpacing + helpTitleHeight
        self.canvas.create_text(textCenter,drawTitleHeight,
                                text='Say "draw" to begin drawing!',
                                fill='blue',
                                font='Helvetica %d bold' % subtitleSize,
                                anchor='s')



################################################################################
#                               Help Mode
################################################################################
    def helpMousePressed(self,event):
        pass
    def helpKeyPressed(self,event):
        if(event.keysym == 'd'):
            self.voiceThread.currentCommand = 'draw'
        if(event.keysym == 'Left'):
            self.helpScreen = 1
        if(event.keysym == 'Right'):
            self.helpScreen = 2
    def helpTimerFired(self):
        if(self.voiceThread.currentCommand == 'draw'):
            self.currentMode = 'draw'
    def helpRedrawAll(self):
        if(self.helpScreen == 1):
            currentHelpScreen = self.helpScreen1
        else:
            currentHelpScreen = self.helpScreen2

        self.canvas.create_image(self.width/2,0,image=currentHelpScreen,anchor='n')
################################################################################
#                               Animation FrameWork
#                              taken from Class Notes
################################################################################

    def run(self, width=1280, height=720):
        # create the self.root and the canvas
        self.root = Tk()
        self.width = width
        self.height = height
        self.root.wm_title("Drawing World")
        self.canvas = Canvas(self.root, width=width, height=height,
                            cursor='pencil')
        self.canvas.pack()


        # set up events
        def redrawAllWrapper():
            self.canvas.delete(ALL)
            self.redrawAll()
            self.canvas.update()

        def mouseReleasedWrapper(event):
            self.mouseReleased(event)
            redrawAllWrapper()

        def mousePressedWrapper(event):
            self.mousePressed(event)
            redrawAllWrapper()

        def mouseMovedWrapper(event):
            self.mouseMoved(event)
            redrawAllWrapper()

        def keyPressedWrapper(event):
            self.keyPressed(event)
            redrawAllWrapper()

        self.root.bind("<ButtonRelease-1>",mouseReleasedWrapper)
        self.root.bind("<B1-Motion>",mouseMovedWrapper)
        self.root.bind("<Button-1>", mousePressedWrapper)
        self.root.bind("<Key>", keyPressedWrapper)

        # set up timerFired events
        self.timerFiredDelay = 10 # milliseconds
        def timerFiredWrapper():
            self.timerFired()
            self.canvas.config(cursor=self.cursorimg)
            redrawAllWrapper()
            # pause, then call timerFired again
            self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
        # init and get timerFired running
        self.init()
        timerFiredWrapper()
        # and launch the app
        self.root.mainloop()
        if(self.camera != None):
            self.camera.release()
        self.voiceThread.kill = True
        print("Bye")


MyWorld = DrawingWorld()
MyWorld.run()
