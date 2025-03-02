import cv2
import pygame
import numpy as np
import math
import mediapipe as mp
import HandTrackingModule as htm
from cvzone.HandTrackingModule import HandDetector


#Functions to detect respective hand gestures. Each function detects one of the 7 hand gestures. if  



# detects distance between left and right hand wrists
def distance_between_wrists(left_list,right_list):
    wrist_dist_x = (left_list[0][0] - right_list[0][0])**2
    wrist_dist_y = (left_list[0][1] - right_list[0][1])**2
    wrist_dist_z = (left_list[0][2] - right_list[0][2])**2
    return (wrist_dist_x + wrist_dist_y + wrist_dist_z)**0.5 #using distance formula

#detects fly motion by checking if right hand's fingers are to the left of the 
#corresponding left hand's fingers and if the wrists are close enough to each other,
#which was determined by a tested treshold. Returns true if both are true
def detect_fly(left_hand,right_hand):
    left_hand_list = left_hand["lmList"]
    right_hand_list = right_hand["lmList"]

    x_coord_indeces = [4,8,12,16,20]

    # if any of the right hand's fingers not to the left of the corresponding left hand finger, return false
    for i in x_coord_indeces:
        if(right_hand_list[i][0] <= left_hand_list[i][0]):
            return False


    wrist_distance = distance_between_wrists(left_hand_list,right_hand_list)
    threshold = 200
    return wrist_distance<threshold
           


#detects throw motion by determining calculating rate of change in the x and y coordinates between 
# the index and pinky fingers. The rate of change is calculated by using a queue. 
# We gathered data every frame and if the change between first and last elements is in range, 
# then a throwing motion was detected. The length of the list was determing based 
# the program's frame rates. 
def detect_throw(hand,zList):
    hand_list = hand["lmList"]
    base_i_x=hand_list[8][0] # index x
    base_i_y=hand_list[8][1] #index y
    base_p_x=hand_list[20][0] # pinky x
    base_p_y=hand_list[20][1] # pink y

    distance = math.dist((base_i_x - base_p_x)(base_i_y - base_p_y))
    zList.append(distance)


    delta_distance = (zList[-1] - zList[0]) // len(zList)

    if (len(zList)>=10):
        zList.pop(0)
    
    threshold = 30
    return delta_distance >=threshold
  



# helper function for fist to palm detection. 
# just calculates distance between every finger tip and its corresponding finger tip (in the y direction) 
# on the other hand and asserts a threshold is met
def fist_palm_tip_help(left_list,right_list):
    finger_tip_indeces = [8,12,16,20] # 8 is index, 12 is middle, 16 is ring, and 20 is pinky
    # 1 = y coordinate
    threshold = 200
    for i in finger_tip_indeces:
        if abs(left_list[i][1]-right_list[i][1])<threshold:
            return False
        
    return True

# same process as above function. 
# Calculates distance based on x and y coordiantes for every set of corresponing fingers, 
# ensuring threshold is met. Uses distance formula 
def fist_palm_knuckle_help(left_hand_list,right_hand_list):
    finger_knuckle_indeces = [5,9,13,17]
    threshold = 200
    for i in finger_knuckle_indeces:
        knuckle_distance = ((left_hand_list[i][0]- right_hand_list[i][0])**2 + 
                            (left_hand_list[i][1]- right_hand_list[i][1])**2) ** 0.5 
        if knuckle_distance >=threshold:
            return False
    
    return True


# uses both helpers to detect motion. 
def detect_fist_palm(left_hand,right_hand):
    left_hand_list = left_hand["lmList"]
    right_hand_list = right_hand["lmList"]
    return fist_palm_tip_help(left_hand_list,right_hand_list) and fist_palm_knuckle_help (left_hand_list,right_hand_list)


# detects dragonBall motion by comparing distances between x and y coordinates of pair of fingers.
# Wrists and x distances should be within threshold, y coordinates should be above a threshold
def detect_dragonBall(left_hand, right_hand):
    left_hand_list = left_hand["lmList"]
    right_hand_list = right_hand["lmList"]
    
    dyIndex = abs(left_hand_list[8][1] - right_hand_list[8][1])
    dxIndex = abs(left_hand_list[8][0]- right_hand_list[8][0])
    
    dyMid = abs(left_hand_list[12][1] - right_hand_list[12][1])
    dxMid = abs(left_hand_list[12][0] - right_hand_list[12][0])
    
    dyRing = abs(left_hand_list[16][1] - right_hand_list[16][1])
    dxRing = abs(left_hand_list[16][0] - right_hand_list[16][0])

    dyPinky = abs(left_hand_list[20][1] - right_hand_list[20][1])
    dxPinky = abs(left_hand_list[20][0] - right_hand_list[20][0])
    
    wristDist = ((left_hand_list[0][0] - right_hand_list[0][0]) ** 2 + 
                 (left_hand_list[0][1] - right_hand_list[0][1]) ** 2) ** 0.5
    

    avgDy = (dyIndex + dyMid + dyRing + dyPinky) / 4
    avgDx = (dxRing + dxPinky + dxMid + dxIndex) / 4

    y_threshold = 500
    wrist_threshold = 200
    x_threshold = 200
    return avgDy >= y_threshold and avgDx <= x_threshold and wristDist <= wrist_threshold




# detect triangle gesture. Distance between thumbs and index fingers should be within threshold.
#index fingers should be directly above the thumbs and go above a minimum threshold
def detect_triangle(left_hand,right_hand):
    left_hand_list = left_hand["lmList"]
    right_hand_list = right_hand["lmList"]

    #calculated using distance formula
    thumb_distance = ((left_hand_list[4][0]- right_hand_list[4][0])**2 + (left_hand_list[4][1]- right_hand_list[4][1])**2) ** 0.5 
    index_distance = ((left_hand_list[8][0]- right_hand_list[8][0])**2 + (left_hand_list[8][1]- right_hand_list[8][1])**2) ** 0.5

    index_avg_y =  (left_hand_list[8][1] + right_hand_list[8][1])//2
    index_avg_x =  (left_hand_list[8][0] + right_hand_list[8][0])//2
    thumb_avg_y =  (left_hand_list[4][1] + right_hand_list[4][1])//2
    thumb_avg_x =  (left_hand_list[4][1] + right_hand_list[4][1])//2

    thumbs_dist_threshold = 150
    index_dist_threshold = 150
    

    return thumb_distance<thumbs_dist_threshold and index_dist_threshold<150 and abs(index_avg_y -thumb_avg_y) > 350 and abs(index_avg_x -thumb_avg_x)<500


#detects catching motion, using a queue to calculate rates of change similar to detect throw
def detect_catch(hand,rev_t_list):
    hand_list = hand["lmList"]
    base_i_x=hand_list[5][0]
    base_i_y=hand_list[5][1]
    base_p_x=hand_list[17][0]
    base_p_y=hand_list[17][1]

    distance = ((base_i_x - base_p_x)**2 + (base_i_y - base_p_y) ** 2)**0.5
    rev_t_list.append(distance)

    delta_distance_rev = (rev_t_list[-1] - rev_t_list[0]) // len(rev_t_list)

    if (len(rev_t_list)>=5):
        rev_t_list.pop(0)


    return delta_distance_rev <=-25

#detects swiping motion that should be used along with the catching motion
def detect_swipe(hand,handX):
    hand_list = hand["lmList"]
    middle_x = hand_list[12][0]

    handX.append(middle_x)

    delta_middle_x = (handX[-1] - handX[0]) // len(handX)

    if(len(handX)>=10): 
        handX.pop(0)

    return(abs(delta_middle_x)>=75)


#takes camera feed and makes the mouse mirror finger movemenents. Returns coordinates where
#mouse should be. Also retruns true if in clicking mode, false otherwise.
def detect_mouse(hand,list_of_fingers,wCam,hCam,wScr,hScr):
    hand_List = hand["lmList"]
    index_tip_x = hand_List[8][0]
    index_tip_y = hand_List[8][1]
    middle_tip_x = hand_List[12][0]
    middle_tip_x_y = hand_List[12][1]

    index_tip_mirrored_x= wScr - index_tip_x

    #only index finger up, no clicking
    if(list_of_fingers[1] ==1 and list_of_fingers[2] == 0): 
        return False,((index_tip_mirrored_x,index_tip_y))
    

    #both index and middle finger pointing, and ring finger should not be up
    elif(list_of_fingers[1] ==1 and list_of_fingers[2] == 1 and list_of_fingers[3] == 0):
        return True, ((index_tip_mirrored_x,index_tip_y))
    
    return False , (0,0)