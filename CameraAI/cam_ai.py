import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import os
import json
import numpy as np
from datetime import datetime

class GestureRecorder:
    def __init__(self):
        self.recorded_gestures = []
        self.is_recording = False
        self.current_gesture = []
        self.gesture_name = ""
        
    def start_recording(self, gesture_name):
        """Start recording a new gesture"""
        self.is_recording = True
        self.current_gesture = []
        self.gesture_name = gesture_name
        print(f"Recording gesture: {gesture_name}")
    
    def stop_recording(self):
        """Stop recording and save the gesture"""
        if self.current_gesture:
            self.recorded_gestures.append({
                'name': self.gesture_name,
                'timestamp': datetime.now().isoformat(),
                'frames': self.current_gesture,
                'num_frames': len(self.current_gesture)
            })
            print(f"Recorded {len(self.current_gesture)} frames for '{self.gesture_name}'")
        self.is_recording = False
        self.current_gesture = []
    
    def add_frame(self, hand_landmarks, frame_shape):
        """Add current hand positions to recording"""
        if not self.is_recording:
            return
        
        h, w, _ = frame_shape
        frame_data = []
        
        for landmark in hand_landmarks:
            landmark_joints = []
            for joint in landmark:
                
        
        self.current_gesture.append(frame_data)
    
    def save_to_file(self, filename="gestures.json"):
        """Save all recorded gestures to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.recorded_gestures, f, indent=2)
        print(f"Saved {len(self.recorded_gestures)} gestures to {filename}")
    
    def load_from_file(self, filename="gestures.json"):
        """Load recorded gestures from a file"""
        with open(filename, 'r') as f:
            self.recorded_gestures = json.load(f)
        print(f"Loaded {len(self.recorded_gestures)} gestures from {filename}")

####################################################################

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "hand_landmarker.task")

# Verify the model file exists
if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    print("Please make sure hand_landmarker.task is in the same folder as this script")
    exit()

print(f"Using model: {model_path}")

# Hand connections for drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)              # Palm connections
]

def to_pixel(x_norm: float, y_norm: float, w: int, h: int) -> tuple[int, int]:
    """Convert normalized coordinates to pixel coordinates"""
    x = min(max(x_norm, 0.0), 1.0)
    y = min(max(y_norm, 0.0), 1.0)
    return int(x * w), int(y * h)

def draw_hand_landmarks(
    image_bgr: np.ndarray,
    hand_landmarks_list,
    connections=HAND_CONNECTIONS,
    draw_points=True,
    draw_connections=True,
    point_radius=3,
    point_thickness=-1,
    line_thickness=2,
):
    """Draw hand landmarks on the image"""
    annotated = image_bgr.copy()
    h, w = annotated.shape[:2]

    for hand_landmarks in hand_landmarks_list:
        # Convert normalized landmarks to pixel coords
        pts = [to_pixel(lm.x, lm.y, w, h) for lm in hand_landmarks]

        if draw_connections:
            for a, b in connections:
                cv2.line(annotated, pts[a], pts[b], (0, 255, 0), line_thickness)

        if draw_points:
            for (x, y) in pts:
                cv2.circle(annotated, (x, y), point_radius, (0, 0, 255), point_thickness)

    return annotated

def count_fingers(hand_landmarks):
    """Count number of raised fingers"""
    # Fingertip landmarks
    tips = [4, 8, 12, 16, 20]
    finger_count = 0
    
    # Thumb (special case - compare x coordinates)
    if hand_landmarks[4].x < hand_landmarks[3].x:
        finger_count += 1
    
    # Other fingers (compare y coordinates)
    for tip in tips[1:]:
        if hand_landmarks[tip].y < hand_landmarks[tip - 2].y:
            finger_count += 1
    
    return finger_count
    

def run_webcam_hand_tracker():
    """Run hand tracking on webcam feed"""
    
    # Initialize the hand landmarker with VIDEO mode
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        running_mode=vision.RunningMode.VIDEO
    )
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Hand tracking started! Press 'q' to quit")

    # Gesture recorder
    gesture_recorder = GestureRecorder()
    is_recording = False
    
    try:
        # Create the landmarker
        with vision.HandLandmarker.create_from_options(options) as landmarker:
            
            while True:
                # Read frame from webcam
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip horizontally for mirror view
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create MediaPipe Image object
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # Get timestamp in milliseconds
                timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
                
                try:
                    # Detect hands in the frame
                    result = landmarker.detect_for_video(mp_image, timestamp_ms)
                except Exception as e:
                    print(f"Detection error: {e}")
                    continue
                
                # Draw hand landmarks if detected
                if result.hand_landmarks:
                    print(f"Type: {type(result.hand_landmarks)}")
                    print(f"Length: {len(result.hand_landmarks)}")
                    print(f"First element type: {type(result.hand_landmarks[0])}")
                    print(f"First element length: {len(result.hand_landmarks[0]) if hasattr(result.hand_landmarks[0], '__len__') else 'not a list'}")
                    print(f"First element coordinates: {result.hand_landmarks[0][0]}")

                    # Draw the landmarks
                    annotated_frame = draw_hand_landmarks(frame, result.hand_landmarks)
                    
                    # Add finger count information
                    for i, hand_landmarks in enumerate(result.hand_landmarks):
                        finger_count = count_fingers(hand_landmarks)
                        
                        # Get wrist position for text placement
                        h, w, _ = frame.shape
                        wrist_x, wrist_y = to_pixel(hand_landmarks[0].x, hand_landmarks[0].y, w, h)
                        
                        # Display finger count
                        cv2.putText(annotated_frame, f"Fingers: {finger_count}", 
                                   (wrist_x, wrist_y - 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        # Get hand type if available
                        if result.handedness and len(result.handedness) > i:
                            hand_type = result.handedness[i][0].category_name
                            cv2.putText(annotated_frame, hand_type, 
                                       (wrist_x, wrist_y - 40),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                else:
                    annotated_frame = frame
                
                # Add info panel
                cv2.rectangle(annotated_frame, (10, 10), (300, 100), (0, 0, 0), -1)
                cv2.putText(annotated_frame, "Hand Tracking Active", (20, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(annotated_frame, "Press 'q' to quit", (20, 65),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Show hand count
                hand_count = len(result.hand_landmarks) if result.hand_landmarks else 0
                cv2.putText(annotated_frame, f"Hands detected: {hand_count}", (20, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Show the frame
                cv2.imshow('Hand Tracking', annotated_frame)
                
                # Break loop on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Break loop on 'r' key to start/stop recording
                if cv2.waitKey(1) & 0xFF == ord('r'):
                    is_recording = not is_recording
                    if is_recording:
                        gesture_recorder.start_recording("New Gesture")
                    else:
                        gesture_recorder.stop_recording()

                # Gesture recorder
                if is_recording:
                    gesture_recorder.add_frame(result.hand_landmarks, annotated_frame.shape)


                    
    except Exception as e:
        print(f"Error in tracker: {e}")
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam closed")

###############################################################


# Run the webcam tracker
if __name__ == "__main__":
    run_webcam_hand_tracker()