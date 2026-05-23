import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.draw = mp.solutions.drawing_utils

    def find_hand_data(self, frame):
        """process the frame and returns the landmark"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        hand_data = None
        if results.multi_hand_landmarks:
            hand_data = results.multi_hand_landmarks[0]
            self.draw.draw_landmarks(frame, hand_data, self.mp_hands.HAND_CONNECTIONS)

        return hand_data, frame