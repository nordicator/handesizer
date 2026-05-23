import cv2
import math
import time
from tracker import HandTracker
from synthesizer import StandaloneSynth

def main():
    tracker = HandTracker()
    synth = StandaloneSynth()
    cap = cv2.VideoCapture(0)

    was_pinched_last_frame = False
    pinch_start_time = 0
    
    current_val_pct = 0
    
    # We use this to save the percentage right before you started moving your hand
    stored_val_pct = 0 
    # Saves the Y position of your hand exactly when you initialized the pinch
    initial_y = 0.0    

    while True:
        success, frame = cap.read()
        if not success: break

        # Get frame height to help calculate a movement boundary box
        frame_height, frame_width, _ = frame.shape

        hand_landmarks, processed_frame = tracker.find_hand_data(frame)

        if hand_landmarks:
            thumb = hand_landmarks.landmark[4]
            index = hand_landmarks.landmark[8]
            
            # 1. Measure distance between only index and thumb
            distance = math.sqrt((index.x - thumb.x)**2 + (index.y - thumb.y)**2 + (index.z - thumb.z)**2)
            is_pinched = distance < 0.045
          
            # 2. Hand just grabbed the virtual knob (Pinch Started)
            if is_pinched and not was_pinched_last_frame:
                pinch_start_time = time.time()  
                # Use the index finger's Y coordinate as our reference anchor point
                initial_y = index.y 
                stored_val_pct = current_val_pct
            
            # 3. Hand released the virtual knob (Pinch Ended)
            elif not is_pinched and was_pinched_last_frame:
                pinch_duration = time.time() - pinch_start_time
                if pinch_duration < 0.4:  
                    synth.cycle_effect_mode()
            
            # 4. Modulating Mode (Holding the pinch and moving vertically)
            if is_pinched:
                pinch_duration = time.time() - pinch_start_time
                if pinch_duration >= 0.4:
                    # Calculate how far you moved up or down from where you initially grabbed
                    # Note: In computer vision, lower Y values mean HIGHER up on the screen!
                    y_delta = initial_y - index.y 
                    
                    # Sensitivity factor: Moving your hand across 35% of the total screen height 
                    # will sweep the dial all the way from 0% to 100%
                    sensitivity = 0.35
                    
                    # Calculate new percentage relative to where your value started
                    calculated_pct = stored_val_pct + int((y_delta / sensitivity) * 100)
                    
                    # Constrain the percentage tightly between 0% and 100%
                    current_val_pct = max(0, min(100, calculated_pct))
                    
                    # Convert percentage back to a 0.0 - 1.0 float value for the synth engine
                    normalized_knob = current_val_pct / 100.0
                    synth.tweak_effect_knob(normalized_knob)

            was_pinched_last_frame = is_pinched

            # --- HUD Overlay Visuals ---
            color = (0, 0, 255) if is_pinched else (0, 255, 0)
            is_modulating = is_pinched and (time.time() - pinch_start_time >= 0.4)
            status_text = "MODULATING (MOVE HAND UP/DOWN)" if is_modulating else "IDLE"
            
            # Draw tracking metadata
            cv2.putText(processed_frame, f"FX Mode: {synth.current_mode.upper()}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(processed_frame, f"Grip: {status_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(processed_frame, f"Value: {current_val_pct}%", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)

            # Draw circle tracking indicators specifically around thumb and index tip
            h, w, _ = processed_frame.shape
            cv2.circle(processed_frame, (int(thumb.x * w), int(thumb.y * h)), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(processed_frame, (int(index.x * w), int(index.y * h)), 8, (255, 0, 255), cv2.FILLED)

        cv2.imshow("Gestural Synth Interface", processed_frame)
        if cv2.waitKey(1) == 27: break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()