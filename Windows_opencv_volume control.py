import cv2
import mediapipe as mp
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volume.GetMute()
volume.GetMasterVolumeLevel()
volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(-20.0, None)

cap = cv2.VideoCapture(0)
hand_detector = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
index_x = 0
index_y = 0
deg = ""
while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks
    if hands !=None:
        index = hands[0].landmark[8]
        thumb = hands[0].landmark[4]
        index_point = [int(index.x*frame_width),int(index.y*frame_height)]
        thumb_point = [int(thumb.x*frame_width),int(thumb.y*frame_height)]
        index_thumb_intersection = [index.x*frame_width,thumb.y*frame_height]
        cv2.circle(frame,(int(index_point[0]),int(index_point[1])),2,(255,0,0),2)
        cv2.circle(frame,(int(thumb_point[0]),int(thumb_point[1])),100,(0,255,0),2)
        cv2.circle(frame,(int(thumb_point[0]),int(thumb_point[1])),40,(0,255,0),2)
        cv2.line(frame,(int(thumb_point[0]+100),int(thumb_point[1])),(int(thumb_point[0]-100),int(thumb_point[1])),(0,0,0),2)
        cv2.line(frame,(int(thumb_point[0]),int(thumb_point[1]+100)),(int(thumb_point[0]),int(thumb_point[1]-100)),(0,0,0),2)
        index_thumb_length = math.sqrt((index_point[0]-thumb_point[0])**2+(index_point[1]-thumb_point[1])**2)
        index_length = math.sqrt((index_point[0]-index_thumb_intersection[0])**2+(index_point[1]-index_thumb_intersection[1])**2)
        thumb_length = math.sqrt((thumb_point[0]-index_thumb_intersection[0])**2+(thumb_point[1]-index_thumb_intersection[1])**2)
        if index_thumb_length < 100 and index_thumb_length > 40:
            new_deg = int(math.degrees(math.atan(index_length/thumb_length))/4)
            if deg!="":
                try:
                    if deg<new_deg:
                        # print("up")
                        volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel()+5.0,None)
                    if deg>new_deg:
                        volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel()-5.0,None)
                        # print("down")
                except:
                    pass
            print(volume.GetMasterVolumeLevel())
            deg = new_deg
            # print(deg)
        
    cv2.imshow('Virtual Mouse', frame)
    cv2.waitKey(1)