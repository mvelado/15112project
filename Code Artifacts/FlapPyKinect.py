from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math

class GameRuntime(object):
    def __init__(self):
        pygame.init()

        self.screen_width = 1920
        self.screen_height = 1080
        self.bird_height = self.screen_height/2
        self.prev_right_hand_height = 0
        self.prev_left_hand_height = 0
        self.cur_right_hand_height = 0
        self.cur_left_hand_height = 0
        self.pipe_x = self.screen_width
        self.flap = 0

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Set the width and height of the window [width/2, height/2]
        self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

        # Loop until the user clicks the close button.
        self._done = False

        # Kinect runtime object, we want color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self._bodies = None

    def draw_bird(self):
        pygame.draw.circle(self._frame_surface, (200,200,0), (int(self.screen_width/2), int(self.screen_height - self.bird_height)), 40)

    def draw_pipes(self):
        # top pipe
        pygame.draw.rect(self._frame_surface, (0, 150, 0), (self.pipe_x, 0, 200, 400))

        # bottom pipe
        pygame.draw.rect(self._frame_surface, (0, 150, 0), (self.pipe_x, self.screen_height - 400, 200, 400))

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def run(self):
        # -------- Main Program Loop -----------
        while not self._done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

            # We have a color frame. Fill out back buffer surface with frame's data 
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            # We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

                if self._bodies is not None: 
                    for i in range(0, self._kinect.max_body_count):
                        body = self._bodies.bodies[i]
                        if not body.is_tracked: 
                            continue 
                    
                        joints = body.joints 
                        # save the hand positions
                        if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.cur_right_hand_height = joints[PyKinectV2.JointType_HandRight].Position.y
                        if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.cur_left_hand_height = joints[PyKinectV2.JointType_HandLeft].Position.y

                        # calculate wing flap
                        self.flap = (self.prev_left_hand_height - self.cur_left_hand_height) + (self.prev_right_hand_height - self.cur_right_hand_height)
                        if math.isnan(self.flap) or self.flap < 0:
                            self.flap = 0

                        # cycle previous and current heights for next time
                        self.prev_left_hand_height = self.cur_left_hand_height
                        self.prev_right_hand_height = self.cur_right_hand_height

            # --- Game logic
            self.bird_height -= 5
            self.bird_height += self.flap * 250
            if self.bird_height <= 0:
                # Don't let the bird fall off the bottom of the screen
                self.bird_height = 0
            if self.bird_height >= self.screen_height:
                # Don't let the bird fly off the top of the screen
                self.bird_height = self.screen_height

            # Move the pipes to the left
            self.pipe_x -= 2
            # When the pipes are past the bird
            if self.pipe_x < 100:
                # Reset the pipes back to the other end of the screen
                self.pipe_x = self.screen_width

            # Draw graphics
            self.draw_bird()
            self.draw_pipes()

            # Optional debugging text
            #font = pygame.font.Font(None, 36)
            #text = font.render(str(self.flap), 1, (0, 0, 0))
            #self._frame_surface.blit(text, (100,100))

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()

game = GameRuntime();
game.run();