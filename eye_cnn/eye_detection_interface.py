# Real-Time Eye Detection Module for AIESIT Integration
# Returns attentiveness state for course video control

import cv2
import numpy as np
from tensorflow import keras
import time
import json

# ===== CONFIGURATION =====
import os

# Get the current directory and set model path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, 'model', 'eye_detection_model.keras')

# Image processing settings
IMG_HEIGHT = 128
IMG_WIDTH = 128

# Face detection parameters
MIN_FACE_SIZE = (60, 60)
MAX_FACE_SIZE = (800, 800)
FACE_SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 4

# Eye detection confidence threshold
EYE_CONFIDENCE_THRESHOLD = 0.70  # Higher threshold for more accurate eye closure detection

# Attentiveness thresholds (adjusted for 30fps)
DROWSY_THRESHOLD = 6      # About 0.2 seconds of closed eyes
SLEEPING_THRESHOLD = 15    # About 0.5 seconds of closed eyes
DISTRACTED_THRESHOLD = 30  # About 1 second without face

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
        
        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Enhance contrast
        gray = cv2.equalizeHist(gray)
        
        # Detect faces with adjusted parameters
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=FACE_SCALE_FACTOR, 
            minNeighbors=MIN_NEIGHBORS,
            minSize=MIN_FACE_SIZE,
            maxSize=MAX_FACE_SIZE
        )
        
        # Keep only largest face
        if len(faces) > 0:
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            faces = [faces[0]]
            self.no_face_count = 0
        else:
            self.no_face_count += 1
            cv2.putText(frame, "No Face Detected", (30, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Process face if detected
        if len(faces) > 0:
            x, y, w, h = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Improved eye region extraction
            eye_height = int(h * 0.30)  # Slightly smaller eye height
            eye_y_start = y + int(h * 0.28)  # Adjusted for better eye position
            
            # Adjusted eye width and position
            left_eye_x = x + int(w * 0.14)
            left_eye_w = int(w * 0.30)
            
            right_eye_x = x + int(w * 0.56)
            right_eye_w = int(w * 0.30)
            
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
                
                # Enhanced image preprocessing
                eye_gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
                
                # Apply multiple enhancements
                eye_enhanced = cv2.equalizeHist(eye_gray)
                eye_enhanced = cv2.GaussianBlur(eye_enhanced, (3, 3), 0)
                
                # Increase contrast
                eye_enhanced = cv2.convertScaleAbs(eye_enhanced, alpha=1.3, beta=0)
                
                eye_img_final = cv2.cvtColor(eye_enhanced, cv2.COLOR_GRAY2BGR)
                
                # Prepare for model
                eye_img_resized = cv2.resize(eye_img_final, (IMG_WIDTH, IMG_HEIGHT))
                eye_img_normalized = eye_img_resized / 255.0
                eye_img_expanded = np.expand_dims(eye_img_normalized, axis=0)
                
                # Calculate eye aspect ratio (EAR)
                eye_height, eye_width = eye_enhanced.shape
                aspect_ratio = float(eye_height) / float(eye_width)
                
                # Predict with enhanced confidence check
                prediction = self.model.predict(eye_img_expanded, verbose=0)[0][0]
                
                # Use both aspect ratio and prediction for more accurate detection
                is_closed = (prediction <= EYE_CONFIDENCE_THRESHOLD) or (aspect_ratio < 0.2)
                
                if not is_closed:
                    status = "OPEN"
                    confidence = int(prediction * 100)
                    color = (0, 255, 0)
                    eye_statuses.append(True)
                else:
                    status = "CLOSED"
                    confidence = int((1 - prediction) * 100)
                    color = (0, 0, 255)
                    eye_statuses.append(False)
                
                # Show eye status with improved positioning
                # Left side for eye name
                cv2.putText(frame, f"{eye_name}:", 
                           (ex, ey-25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, color, 1)
                
                # Right side for status and confidence
                cv2.putText(frame, f"{status} ({confidence}%)", 
                           (ex, ey-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, color, 1)
            
            # Update counters with more responsive state management
            if len(eye_statuses) >= 2:
                closed_eyes = sum(not status for status in eye_statuses)
                
                if closed_eyes >= 2:  # Both eyes closed
                    self.closed_count += 2
                    self.open_count = 0  # Reset open counter
                elif closed_eyes == 1:  # One eye closed
                    self.closed_count += 1
                    self.open_count = 0  # Reset open counter
                else:  # Both eyes open
                    self.open_count += 1
                    # Quick reset of closed counter when eyes are definitely open
                    if self.open_count >= 2:
                        self.closed_count = 0
            
            # Add debug information with more details
            status_color = (0, 0, 255) if self.closed_count > DROWSY_THRESHOLD else (255, 255, 255)
            cv2.putText(frame, f"Closed frames: {self.closed_count}", 
                       (10, frame.shape[0] - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Determine state based on thresholds with more aggressive state changes
        previous_state = self.current_state
        
        if self.no_face_count > DISTRACTED_THRESHOLD:
            self.current_state = "DISTRACTED"
            cv2.putText(frame, "WARNING: Face not detected!", 
                       (frame.shape[1]//2 - 150, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        elif self.closed_count > SLEEPING_THRESHOLD:
            self.current_state = "SLEEPING"
            cv2.putText(frame, "ALERT: Subject is Sleeping!", 
                       (frame.shape[1]//2 - 150, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            # Add an additional alert box
            cv2.rectangle(frame, (50, 40), (frame.shape[1]-50, 80), (0, 0, 255), 2)
            if self.current_state != "SLEEPING":
                self.sleeping_events += 1
        elif self.closed_count > DROWSY_THRESHOLD:
            self.current_state = "DROWSY"
            cv2.putText(frame, "Warning: Getting Drowsy!", 
                       (frame.shape[1]//2 - 150, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            if self.current_state != "DROWSY":
                self.drowsy_events += 1
        elif self.open_count >= 2:  # Reduced threshold for attentive state
            self.current_state = "ATTENTIVE"
            self.closed_count = 0  # Reset closed count when definitely attentive
        
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