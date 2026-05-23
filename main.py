import cv2 
from tracker import HandTracker
from synthesizer import StandaloneSynth


def main():
    tracker = HandTracker()
    synth = StandaloneSynth()

    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success: break

        # graber the data
        hand_landmarks, processed_frame = tracker.find_hand_data(frame)

        if hand_landmarks:

            index_y = hand_landmarks.landmark[8].y

            modulation_value = 1.0 - index_y
            synth.modulate_filter(modulation_value)

        cv2.imshow("hand tracking synth", processed_frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


# cap = cv2.VideoCapture(0)

# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands()
# draw = mp.solutions.drawing_utils

# while True:
#     success, frame = cap.read()
#     if not success:
#         print("failed to grab frame")
#         break

#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = hands.process(rgb)

#     if results.multi_hand_landmarks:
#         for hand in results.multi_hand_landmarks:
#             draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

#     cv2.imshow("handtracking", frame)

#     if cv2.waitKey(1) == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()