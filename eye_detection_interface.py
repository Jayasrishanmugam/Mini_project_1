# Real-Time Eye Detection Module for AIESIT Integration
# Returns attentiveness state for course video control

import cv2
import numpy as np
from tensorflow import keras
import time
import json

# ===== CONFIGURATION =====
MODEL_PATH = 'C:/Users/Aravindan/CNN_MODEL/model/eye_detection_model.keras'
IMG_HEIGHT = 128
IMG_WIDTH = 128

# Attentiveness thresholds
DROWSY_THRESHOLD = 10     # Frames with closed eyes to trigger drowsy state (about 1 second at 30fps)
SLEEPING_THRESHOLD = 30     # Frames with closed eyes to trigger sleeping state (about 3 seconds)
DISTRACTED_THRESHOLD = 45   # Frames without face detection to trigger distracted state (about 2 seconds)

class EyeDetectionMonitor:
    """
    Eye Detection Monitor for Student Attentiveness
    Returns state: ATTENTIVE, DROWSY, SLEEPING, or DISTRACTED
    """
    
    def __init__(self, model_path):
        print("Loading eye detection model...")
        self.model = keras.models.load_model(model_path)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # State tracking
        self.closed_count = 0
        self.open_count = 0
        self.no_face_count = 0
        self.current_state = "ATTENTIVE"
        self.last_state_change = time.time()
        
        # Statistics
        self.total_frames = 0
        self.drowsy_events = 0
        self.sleeping_events = 0
        self.distracted_events = 0
        
        print("Eye detection monitor initialized!")
    
    def get_state(self):
        """Returns current attentiveness state"""
        return {
            "state": self.current_state,
            "closed_frames": self.closed_count,
            "no_face_frames": self.no_face_count,
            "timestamp": time.time(),
            "requires_interaction": self.current_state in ["SLEEPING", "DISTRACTED"],
            "should_pause_video": self.current_state in ["SLEEPING", "DISTRACTED"]
        }
    
    def get_statistics(self):
        """Returns session statistics"""
        return {
            "total_frames": self.total_frames,
            "drowsy_events": self.drowsy_events,
            "sleeping_events": self.sleeping_events,
            "distracted_events": self.distracted_events,
            "current_state": self.current_state
        }
    
    def process_frame(self, frame):
        """
        Process a single frame and update state
        Returns: (processed_frame, state_dict)
        """
        self.total_frames += 1
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=5, 
            minSize=(80, 80), maxSize=(500, 500)
        )
        
        # Keep only largest face
        if len(faces) > 0:
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            faces = [faces[0]]
            self.no_face_count = 0
        else:
            self.no_face_count += 1
        
        # Process face if detected
        if len(faces) > 0:
            x, y, w, h = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Extract eye regions
            eye_height = int(h * 0.35)
            eye_y_start = y + int(h * 0.25)
            
            left_eye_x = x + int(w * 0.12)
            left_eye_w = int(w * 0.35)
            
            right_eye_x = x + int(w * 0.53)
            right_eye_w = int(w * 0.35)
            
            eye_regions = [
                ("Left", left_eye_x, eye_y_start, left_eye_w, eye_height),
                ("Right", right_eye_x, eye_y_start, right_eye_w, eye_height)
            ]
            
            eye_statuses = []
            
            for eye_name, ex, ey, ew, eh in eye_regions:
                cv2.rectangle(frame, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 1)
                
                eye_img = frame[ey:ey+eh, ex:ex+ew]
                
                if eye_img.size == 0:
                    continue
                
                # Enhance image
                eye_gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
                eye_enhanced = cv2.equalizeHist(eye_gray)
                eye_img_final = cv2.cvtColor(eye_enhanced, cv2.COLOR_GRAY2BGR)
                
                eye_img_resized = cv2.resize(eye_img_final, (IMG_WIDTH, IMG_HEIGHT))
                eye_img_normalized = eye_img_resized / 255.0
                eye_img_expanded = np.expand_dims(eye_img_normalized, axis=0)
                
                # Predict
                prediction = self.model.predict(eye_img_expanded, verbose=0)[0][0]
                
                if prediction > 0.6:
                    status = "OPEN"
                    color = (0, 255, 0)
                    eye_statuses.append(True)
                else:
                    status = "CLOSED"
                    color = (0, 0, 255)
                    eye_statuses.append(False)
                
                cv2.putText(frame, f"{eye_name}: {status}", 
                           (ex, ey-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.4, color, 1)
            
            # Update counters with smoothing
            if len(eye_statuses) >= 2:
                if not any(eye_statuses):  # Both eyes closed
                    self.closed_count += 1
                    self.open_count = 0
                else:  # At least one eye open
                    self.open_count += 1
                    if self.open_count >= 1:
                        self.closed_count = 0
        
        # Determine state based on thresholds
        previous_state = self.current_state
        
        if self.no_face_count > DISTRACTED_THRESHOLD:
            self.current_state = "DISTRACTED"
        elif self.closed_count > SLEEPING_THRESHOLD:
            self.current_state = "SLEEPING"
        elif self.closed_count > DROWSY_THRESHOLD:
            self.current_state = "DROWSY"
        else:
            self.current_state = "ATTENTIVE"
        
        # Track state changes and events
        if previous_state != self.current_state:
            self.last_state_change = time.time()
            if self.current_state == "DROWSY":
                self.drowsy_events += 1
            elif self.current_state == "SLEEPING":
                self.sleeping_events += 1
            elif self.current_state == "DISTRACTED":
                self.distracted_events += 1
        
        # Draw UI based on state
        self._draw_ui(frame, len(faces) > 0)
        
        return frame, self.get_state()
    
    def _draw_ui(self, frame, face_detected):
        """Draw UI elements on frame"""
        # State indicator
        state_colors = {
            "ATTENTIVE": (0, 255, 0),
            "DROWSY": (0, 165, 255),
            "SLEEPING": (0, 0, 255),
            "DISTRACTED": (255, 0, 255)
        }
        
        color = state_colors.get(self.current_state, (255, 255, 255))
        
        # Alert for sleeping/distracted
        if self.current_state in ["SLEEPING", "DISTRACTED"]:
            message = "ALERT: STUDENT NOT ATTENTIVE!" if self.current_state == "SLEEPING" else "ALERT: STUDENT DISTRACTED!"
            cv2.putText(frame, message, 
                       (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       1.2, (0, 0, 255), 3)
            cv2.rectangle(frame, (10, 10), (630, 470), (0, 0, 255), 5)
        
        # Status bar
        status_text = f"State: {self.current_state}"
        if face_detected:
            status_text += f" | Closed: {self.closed_count}"
        else:
            status_text += f" | No Face: {self.no_face_count}"
        
        cv2.putText(frame, status_text, 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, color, 2)
        
        # Instructions
        cv2.putText(frame, "Press 'q' to quit | 's' for screenshot | 'r' for stats", 
                   (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (255, 255, 255), 1)


# ===== STANDALONE MODE (for testing) =====
def run_standalone():
    """Run as standalone application"""
    monitor = EyeDetectionMonitor(MODEL_PATH)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot access webcam")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    
    print("\n=== Eye Detection Monitor Started ===")
    print("States: ATTENTIVE -> DROWSY -> SLEEPING")
    print("=" * 40)
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame")
            break
        
        # Process frame
        processed_frame, state = monitor.process_frame(frame)
        
        # Show frame
        cv2.imshow('AIESIT - Eye Detection Monitor', processed_frame)
        
        # Print state changes
        if state['requires_interaction']:
            print(f"\n>>> INTERACTION REQUIRED: {state['state']} <<<")
            print(f"    Video should be paused!")
            print(f"    Timestamp: {time.strftime('%H:%M:%S')}")
        
        # Key controls
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\nQuitting...")
            break
        elif key == ord('s'):
            filename = f"screenshot_{int(time.time())}.jpg"
            cv2.imwrite(filename, processed_frame)
            print(f"Screenshot saved: {filename}")
        elif key == ord('r'):
            stats = monitor.get_statistics()
            print(f"\n--- Session Statistics ---")
            print(f"Total Frames: {stats['total_frames']}")
            print(f"Drowsy Events: {stats['drowsy_events']}")
            print(f"Sleeping Events: {stats['sleeping_events']}")
            print(f"Distracted Events: {stats['distracted_events']}")
            print(f"Current State: {stats['current_state']}")
            print("-" * 26)
    
    # Final statistics
    print("\n=== Final Session Statistics ===")
    stats = monitor.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_standalone()