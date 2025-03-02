import cv2
import pygame
import numpy as np
import mediapipe as mp
import pygame
import app
from screens import *
from trainer import *
from player_mon import *
from opponent_mon import *
from text_box import *
from main import *


import HandTrackingModule as htm
from cvzone.HandTrackingModule import HandDetector

from func import *

last_update = pygame.time.get_ticks() 
clock = pygame.time.Clock()
# Initialize Pygame
pygame.init()

# Set up display
screen_width, screen_height = 900, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Test Poses for Pokémon")

# Initialize OpenCV camera
cap = cv2.VideoCapture(0)  # Use 0 for default webcam
cap.set(cv2.CAP_PROP_FRAME_WIDTH,screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,screen_height)


# Get original camera feed dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame = cv2.flip(cap.read()[1], 1)  # Read and flip in one line
aspect_ratio = frame_width /frame_height

# Define target size for camera feed in Pygame
target_height = screen_height//4   # 1/4 of screen height
target_width = int(target_height * aspect_ratio)  # Maintain aspect ratio

# Initialize Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

# Define the target sequence of gestures
move_list = ["Fly", "fist_palm","dragonBall","Triangle"]

special_list= ["Catch","Swipe","Throw","Exit_sequence"]

# Initialize variables for sequence recognition
sequence_buffer = []  # Stores detected gestures
sequence_index = 0    # Tracks progress in target sequence
buffer_size = 30      # Buffer size


# Main Loop
running = True
zL = [] # for throw calc
zR = []
left_is_throwing = False
right_is_throwing = False


#for reverse throw
zL_rev = []
zR_rev=[]
left_is_catching = False
right_is_catching = False


#for swipe
LHX = []
RHX = []
right_is_swiping = False
left_is_swiping = False

sequence_complete = False
just_caught = True


def display_mouse(coordinates, color):
    x,y = coordinates
    pygame.draw.circle(screen,color,(x,y),10,2)



mouseX = screen_width // 2
mouseY = screen_height // 2
mousePressed = False
pygame.mouse.set_pos(mouseX, mouseY)
# delay  = - 1
wait = 5
while running:
    screen.fill((0,0,0))
    app.canvas.blit(app.bg, (0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if app.in_start and pressedStart(event.pos):
                toGuide()
            elif (app.in_win or app.in_lose) and pressedPlayAgain(event.pos):
                toStart()
                app.reset()
            elif app.in_guide and pressedGotIt(event.pos):
                toSelect()
            elif app.in_select:
                if pressedBack(event.pos):
                    toStart()
                if hoverBulb(event.pos):
                    if not(app.bulbDead):
                        toBattle()
                        if not(app.pickBulb):
                            app.trainer = Trainer()
                        app.pickChar = False
                        app.pickBulb = True
                        app.pickSquirt = False
                        app.curr_pokemon_dead = False
                elif hoverChar(event.pos): 
                    if not(app.charDead):
                        toBattle()
                        if not(app.pickChar):
                            app.trainer = Trainer()
                        app.pickChar = True
                        app.pickBulb = False
                        app.pickSquirt = False
                        app.curr_pokemon_dead = False
                elif hoverSquirt(event.pos): 
                    if not(app.squirtDead):
                        toBattle()
                        if not(app.pickSquirt):
                            app.trainer = Trainer()
                        app.pickChar = False
                        app.pickBulb = False
                        app.pickSquirt = True
                        app.curr_pokemon_dead = False
        elif event.type == pygame.KEYDOWN: #temporary for fainting pokemon and going to end screen
            if event.key == pygame.K_r:
                app.reset()
                toStart()
    
    
    # Handle Pygame event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Capture frame from OpenCV
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    # Flip frame horizontally for mirror effect
 
    # Convert frame from BGR (OpenCV) to RGB (MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands using cvzone
    hands_detected, img = detector.findHands(frame, draw=True)

    # Initialize detected gesture
    current_gesture = "None"

    left_hand = None
    right_hand = None
    # if (delay>=0):
    #     delay -=1



    if hands_detected:
        for hand in hands_detected:
            if hand["type"] == "Left":
                left_hand = hand

                
            else:
                right_hand = hand
        
            hand_type = hand["type"]

            # Display hand type on screen
            bbox = hand["bbox"]
            cv2.putText(frame, f"{hand_type} Hand", (bbox[0], bbox[1] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if len(hands_detected) == 1:
            hand = hands_detected[0]
            isClick ,coord = detect_mouse(hand,detector.fingersUp(hand),target_width,target_height,screen_width,screen_height)
            # print(type(coord))
            if not isClick:
                app.mousePressed = False
                wait = 5
                # print("COORD",coord)
                # print("COORD00000", coord[0])
                app.mouseX = coord[0]
                # print("MOUSE XXXXX", mouseX)
                app.mouseY = coord[1]
                display_mouse(coord, 'white')
            else:
                app.mouseX = coord[0]
                app.mouseY = coord[1]
                wait -= 1
                if wait == 0:
                    app.mousePressed = True
                if app.in_start and pressedStart((app.mouseX, app.mouseY)):
            
            #pygame.mouse.set_pos(200,300)
            
            
    if mouseX <= 0:
        mouseX = 1
    elif mouseX >= screen_width:
        mouseX = screen_width - 1
    if mouseY <= 0:
        mouseY = 1
    elif mouseY >= screen_height:
        mouseY = screen_height - 1
    
    
    pygame.mouse.set_pos((mouseX,mouseY))
    print(pygame.mouse.get_pos())
    

    if (right_hand):
        # print('RIGHT',right_hand != {})
        # print('ZR>>>>>>',zR == [])
        # if (delay<=-1):
        right_is_throwing = detect_throw(right_hand,zR)
        right_is_catching = detect_catch(right_hand,zR_rev)
        right_is_swiping= detect_swipe(right_hand,RHX)
        
    

    # else:
    #     zR = []
    if(left_hand):
        # print('Left',left_hand != {})
        # if (delay<=-1):
        left_is_throwing = detect_throw(left_hand,zL)
        left_is_catching = detect_catch(left_hand,zL_rev)
        left_is_swiping = detect_swipe(left_hand,LHX)
    # else:
    #     zL = []

    is_throwing = left_is_throwing or right_is_throwing
    is_catching = right_is_catching or left_is_catching
    is_swiping = right_is_swiping or left_is_swiping


    if is_throwing:
        # print(is_throwing)
        # delay = 50
        current_gesture = special_list[2]
    elif is_catching:
        current_gesture  = special_list[0]
        just_caught = True
    if just_caught == True and is_swiping:
        current_gesture = special_list[1]
        sequence_complete= True
        current_gesture = special_list[3]


    if left_hand and right_hand:
        if (detect_fly(left_hand,right_hand)):
            current_gesture = move_list[0]
            print("FLY", current_gesture)
        elif (detect_fist_palm(left_hand,right_hand)):
            current_gesture = move_list[1]
        elif (detect_dragonBall(left_hand,right_hand)):
            current_gesture = move_list[2]
        elif (detect_triangle(left_hand,right_hand)):
            current_gesture = move_list[3]
    print(current_gesture)
    

    # Update the sequence buffer
    # if current_gesture != "None":
    #     sequence_buffer.append(current_gesture)

    #     # Keep buffer size manageable
    #     if len(sequence_buffer) > buffer_size:
    #         sequence_buffer.pop(0)

        


  



    # Convert frame from BGR (OpenCV) to RGB (Pygame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Resize frame to fit Pygame screen
    frame = cv2.resize(frame, (target_width, target_height))

    # Convert frame to Pygame surface
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)

    # Display camera feed on Pygame screen
    screen.blit(frame, (0, 0))

    # Display sequence progress
    font = pygame.font.Font(None, 36)
    text = font.render(f"Current Move:{current_gesture}", True, (255, 255, 255))
    #screen.blit(text, (screen_width // 2 - 150, screen_height - 50))

    if app.in_battle:
                if event.key == pygame.K_BACKSPACE:
                    toSelect()
                if app.curr_pokemon == None: # spawn in opponent and player
                    if event.key == pygame.K_SPACE:
                        app.trainer.throwing_ball = True
                        throw_ball()
                        spawn_player_mon()
                        if app.opponent == None: spawn_opponent()
                else:
                    # player attacks
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4) and app.opponent:
                        use_player_move(event)
                    # opponent attacks
                    elif event.key == pygame.K_h and app.curr_pokemon.hp > 0 and app.opponent != None:
                        use_opponent_move()
                    if app.hit_opponent_animation_active and app.opponent:
                        hit_opponent()
                    if app.hit_player_animation_active:
                        hit_player()

    if app.in_battle:
        app.current_time = pygame.time.get_ticks()
        
        if app.trainer.showing:
            throw_ball()
            app.canvas.blit(app.trainer.animation[app.trainer.frame_index], (app.trainer.x, app.canvas_height - 300))

        if app.curr_pokemon is not None: draw_player_mon()

        if app.opponent is not None: draw_opponent_mon()

        if app.text_box_active: draw_text_box()

        if app.charDead and app.squirtDead and app.bulbDead: toLose()
        elif app.opponent_dead: toWin()
        elif app.curr_pokemon_dead: toSelect()

    if app.in_select:
        mousePos = pygame.mouse.get_pos()
        instr_text, instr_rect = app.pokefont.render("CLICK TO CHOOSE", (0,0,0), size = 18)
        instr_rect.center = (450, 535)
        app.canvas.blit(instr_text, instr_rect)

        if hoverBulb(mousePos):
            app.canvas.blit(app.arrowImg, (140, 180))
            if app.bulbDead:
                warn_text, warn_rect = app.pokefont.render("FAINTED! CAN'T CHOOSE", (0,0,0), size = 18)
                warn_rect.center = (450, 565)
                app.canvas.blit(warn_text, warn_rect)
        elif hoverChar(mousePos):
            app.canvas.blit(app.arrowImg, (405, 180))
            if app.charDead:
                warn_text, warn_rect = app.pokefont.render("FAINTED! CAN'T CHOOSE", (0,0,0), size = 18)
                warn_rect.center = (450, 565)
                app.canvas.blit(warn_text, warn_rect)
        elif hoverSquirt(mousePos):
            app.canvas.blit(app.arrowImg, (680, 180))
            if app.squirtDead:
                warn_text, warn_rect = app.pokefont.render("FAINTED! CAN'T CHOOSE", (0,0,0), size = 18)
                warn_rect.center = (450, 565)
                app.canvas.blit(warn_text, warn_rect)
                
        else:
            app.canvas.fill((0, 0, 0))
            app.canvas.blit(app.bg, (0,0))

        if app.bulbDead:
            app.canvas.blit(app.bulbDeadImg, (88, 245))
        else:
            app.canvas.blit(app.bulbImg, (88, 245))
        
        if app.charDead:
            app.canvas.blit(app.charDeadImg, (375, 240))
        else: 
            app.canvas.blit(app.charImg, (375, 240))
        
        if app.squirtDead:
            app.canvas.blit(app.squirtDeadImg, (625, 240))
        else:
            app.canvas.blit(app.squirtImg, (625, 240))

    if app.opponent_dead: pass

    app.window.blit(app.canvas, (0,0))
    screen.blit(frame, (0, 0))
    pygame.display.update()
    clock.tick(60)


    
    # Update Pygame display
    pygame.display.flip()

    # Cap frame rate 
    pygame.time.Clock().tick(60)

# Release resources and quit Pygame
cap.release()
pygame.quit()
