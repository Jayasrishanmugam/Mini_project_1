"""
Integrated AI English Speaking Interactive Training System
Combines Posture Detection and Eye Detection in parallel threads
"""

import threading
import cv2
import time
import os
import numpy as np
from openpose.posture_detection import PostureDetector
from eye_cnn.eye_detection_interface import EyeDetectionMonitor

class IntegratedSystem:
    def __init__(self):
        self.running = False
        
        # Initialize posture detector with improved settings
        self.posture_detector = PostureDetector()
        
        # Initialize eye monitor with correct model path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'eye_cnn', 'model', 'eye_detection_model.keras')
        self.eye_monitor = EyeDetectionMonitor(model_path)
        
        # Shared state with thread safety
        self.lock = threading.Lock()
        self.eye_state = "ATTENTIVE"
        self.posture_state = "NOT_VISIBLE"  # Default to not visible
        
        # Thread management
        self.posture_thread = None
        self.eye_thread = None
        self.status_thread = None
        
        # Camera handles
        self.posture_cap = None
        self.eye_cap = None
        
        # Performance monitoring
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.fps = 0
    
    def run_posture_detection(self):
        """Thread function for posture detection - COMMENTED OUT FOR GUI IMPLEMENTATION"""
        print("⚠️ Posture detection is currently disabled for GUI implementation")
        return
        
        # COMMENTED OUT - OpenPose Implementation
        # self.posture_cap = cv2.VideoCapture(0)
        # 
        # if not self.posture_cap.isOpened():
        #     print("❌ Error: Could not open camera for posture detection")
        #     return
        #     
        # # Optimize camera settings for posture detection
        # self.posture_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # self.posture_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # self.posture_cap.set(cv2.CAP_PROP_FPS, 30)
        # 
        # print("🎥 Posture detection camera opened successfully")
        # 
        # # Create named window and move it
        # cv2.namedWindow('Posture Detection', cv2.WINDOW_NORMAL)
        # cv2.moveWindow('Posture Detection', 0, 0)
        # 
        # try:
        #     while self.running:
        #         success, image = self.posture_cap.read()
        #         if not success:
        #             continue
        #         
        #         # Calculate FPS
        #         self.frame_count += 1
        #         if time.time() - self.last_fps_time >= 1.0:
        #             self.fps = self.frame_count
        #             self.frame_count = 0
        #             self.last_fps_time = time.time()
        #         
        #         # Flip image horizontally for selfie view
        #         image = cv2.flip(image, 1)
        #         
        #         # Convert BGR to RGB for MediaPipe
        #         image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #         
        #         # Process the image with MediaPipe Pose
        #         results = self.posture_detector.pose.process(image_rgb)
        #         
        #         # Draw pose landmarks and analyze
        #         if results.pose_landmarks:
        #             # Draw the pose annotation on the image
        #             self.posture_detector.mp_drawing.draw_landmarks(
        #                 image,
        #                 results.pose_landmarks,
        #                 self.posture_detector.mp_pose.POSE_CONNECTIONS,
        #                 landmark_drawing_spec=self.posture_detector.mp_drawing_styles.get_default_pose_landmarks_style()
        #             )
        #             
        #             # Analyze posture with improved feedback
        #             is_good_posture, feedback, angles = self.posture_detector.analyze_posture(
        #                 results.pose_landmarks.landmark
        #             )
        #             
        #             # Update posture state with thread safety
        #             with self.lock:
        #                 self.posture_state = "GOOD POSTURE" if is_good_posture else "BAD POSTURE"
        #             
        #             # Draw enhanced posture information
        #             image = self.posture_detector.draw_posture_info(image, is_good_posture, feedback, angles)
        #             
        #             # Update statistics with thread safety
        #             current_time = time.time()
        #             time_diff = current_time - self.posture_detector.last_time
        #             if is_good_posture:
        #                 self.posture_detector.good_posture_time += time_diff
        #             else:
        #                 self.posture_detector.bad_posture_time += time_diff
        #             self.posture_detector.last_time = current_time
        #             
        #         # Add FPS counter
        #         cv2.putText(image, f"FPS: {self.fps}", (10, 30), 
        #                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #         
        #         cv2.imshow('Posture Detection', image)
        #         
        #         if cv2.waitKey(5) & 0xFF == ord('q'):
        #             break
        #         
        # finally:
        #     if self.posture_cap is not None:
        #         self.posture_cap.release()
        #     cv2.destroyWindow('Posture Detection')
    
    def run_eye_detection(self):
        """Thread function for eye detection"""
        self.eye_cap = cv2.VideoCapture(0)
        
        if not self.eye_cap.isOpened():
            print("❌ Error: Could not open camera for eye detection")
            return
            
        # Optimize camera settings for eye detection
        self.eye_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.eye_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.eye_cap.set(cv2.CAP_PROP_FPS, 30)
        self.eye_cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.eye_cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)  # Increased brightness
        self.eye_cap.set(cv2.CAP_PROP_CONTRAST, 150)  # Increased contrast
        
        # Create named window and move it
        cv2.namedWindow('Eye Detection', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Eye Detection', 650, 0)
        
        print("🎥 Eye detection camera opened successfully")
        
        try:
            frames_without_face = 0
            last_detection_time = time.time()
            
            while self.running:
                ret, frame = self.eye_cap.read()
                if not ret:
                    continue
                
                # Process frame with eye detection
                processed_frame, state = self.eye_monitor.process_frame(frame)
                
                # Enhanced state handling with improved timing
                with self.lock:
                    prev_state = self.eye_state
                    current_time = time.time()
                    
                    # Handle face detection failures
                    if state.get('no_face_frames', 0) > 15:  # Reduced threshold for faster response
                        if current_time - last_detection_time > 2.0:  # Give 2 seconds before marking as distracted
                            self.eye_state = "DISTRACTED"
                            frames_without_face += 1
                            # Add warning text to frame
                            cv2.putText(processed_frame, "⚠️ No Face Detected!", 
                                      (int(processed_frame.shape[1]/2)-150, 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    else:
                        frames_without_face = 0
                        last_detection_time = current_time
                        self.eye_state = state['state']
                    
                    # Add state transition alert with improved visibility
                    if prev_state != self.eye_state:
                        alert_color = (0, 0, 255) if self.eye_state in ["SLEEPING", "DISTRACTED"] else \
                                    (0, 165, 255) if self.eye_state == "DROWSY" else \
                                    (0, 255, 0)
                        cv2.putText(processed_frame, f"State Change → {self.eye_state}", 
                                  (10, processed_frame.shape[0] - 20),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, alert_color, 2)
                
                # Enhanced status display
                state_color = (0, 0, 255) if self.eye_state in ["SLEEPING", "DISTRACTED"] else \
                            (0, 165, 255) if self.eye_state == "DROWSY" else \
                            (0, 255, 0)
                
                # Add state info box
                cv2.rectangle(processed_frame, (5, 35), (300, 85), (0, 0, 0), -1)
                cv2.putText(processed_frame, f"Eye State: {self.eye_state}", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.7, state_color, 2)
                
                # Add closed eyes counter when relevant
                if state.get('closed_frames', 0) > 0:
                    cv2.putText(processed_frame, 
                              f"Eyes Closed: {state.get('closed_frames', 0)} frames", 
                              (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.6, (0, 165, 255), 2)
                
                cv2.imshow('Eye Detection', processed_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                    break
                
        finally:
            if self.eye_cap is not None:
                self.eye_cap.release()
            cv2.destroyWindow('Eye Detection')
    
    def display_status(self):
        """Thread function for displaying combined status"""
        status_window = np.zeros((400, 1000, 3), dtype=np.uint8)
        
        # Status colors
        GREEN = (0, 255, 0)
        RED = (0, 0, 255)
        YELLOW = (0, 255, 255)
        WHITE = (255, 255, 255)
        ORANGE = (0, 165, 255)
        
        while self.running:
            # Create fresh status window
            status_window.fill(0)
            
            # Get current states with thread safety
            with self.lock:
                eye_state = self.eye_state
                posture_state = self.posture_state
                
            # Track alert conditions
            is_sleeping = (eye_state == "SLEEPING" or posture_state == "SLEEPING")
            is_distracted = (eye_state == "DISTRACTED" or posture_state == "NOT_VISIBLE")
            bad_posture = posture_state == "BAD_POSTURE"
            
            # Display title
            cv2.putText(status_window, "AI English Speaking Training System", 
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, WHITE, 2)
            
            # Title with overall status
            title_color = RED if (is_sleeping or is_distracted) else \
                         YELLOW if bad_posture else GREEN
            cv2.putText(status_window, "AI English Speaking Training System", 
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, title_color, 2)
            
            # Display eye state with enhanced color coding
            eye_color = GREEN if eye_state == "ATTENTIVE" else \
                       YELLOW if eye_state == "DROWSY" else \
                       ORANGE if eye_state == "DISTRACTED" else RED
            cv2.putText(status_window, f"Eye State: {eye_state}", 
                       (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, eye_color, 2)
            
            # Display detailed posture state
            posture_color = GREEN if posture_state == "GOOD_POSTURE" else \
                          RED if posture_state == "SLEEPING" else \
                          ORANGE if posture_state == "NOT_VISIBLE" else YELLOW
            cv2.putText(status_window, f"Posture State: {posture_state}", 
                       (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, posture_color, 2)
            
            # Get statistics
            eye_stats = self.eye_monitor.get_statistics()
            total_time = self.posture_detector.good_posture_time + \
                        self.posture_detector.bad_posture_time + \
                        self.posture_detector.sleeping_time
            
            # Display enhanced statistics
            cv2.putText(status_window, f"Session Statistics:", 
                       (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.8, WHITE, 2)
                       
            if total_time > 0:
                # Posture percentages
                good_posture_percent = (self.posture_detector.good_posture_time/total_time*100)
                bad_posture_percent = (self.posture_detector.bad_posture_time/total_time*100)
                sleeping_percent = (self.posture_detector.sleeping_time/total_time*100)
                
                cv2.putText(status_window, 
                           f"Good Posture: {good_posture_percent:.1f}% | " +
                           f"Bad Posture: {bad_posture_percent:.1f}% | " +
                           f"Sleeping: {sleeping_percent:.1f}%", 
                           (40, 230), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, WHITE, 2)
            
            # Display attention alerts
            y_pos = 280
            if is_sleeping:
                cv2.putText(status_window, "🛑 CRITICAL ALERT: Student is Sleeping!", 
                           (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, RED, 2)
                y_pos += 40
            
            if is_distracted:
                cv2.putText(status_window, "⚠️ WARNING: Student is Distracted/Not Visible", 
                           (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, ORANGE, 2)
                y_pos += 40
            
            if bad_posture and not is_sleeping:
                cv2.putText(status_window, "⚠️ ALERT: Poor Posture Detected", 
                           (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, YELLOW, 2)
                
            # Display eye statistics
            cv2.putText(status_window, 
                       f"Eye Events - Drowsy: {eye_stats['drowsy_events']} | " + 
                       f"Sleep: {eye_stats['sleeping_events']} | " +
                       f"Distracted: {eye_stats['distracted_events']}", 
                       (20, 360), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, WHITE, 2)
            
            cv2.imshow('System Status', status_window)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(0.1)  # Reduce CPU usage
        
        cv2.destroyWindow('System Status')
    
    def run(self):
        """Start the integrated system"""
        print("="*60)
        print("🎯 AI ENGLISH SPEAKING INTERACTIVE TRAINING SYSTEM")
        print("Integrated Posture and Eye Detection")
        print("="*60)
        print("\nPress 'q' in any window to quit")
        print("="*60)
        
        self.running = True
        
        # Create threads
        self.posture_thread = threading.Thread(target=self.run_posture_detection)
        self.eye_thread = threading.Thread(target=self.run_eye_detection)
        self.status_thread = threading.Thread(target=self.display_status)
        
        # Set as daemon threads so they'll be forced to quit with main thread
        self.posture_thread.daemon = True
        self.eye_thread.daemon = True
        self.status_thread.daemon = True
        
        try:
            # Start threads
            self.posture_thread.start()
            self.eye_thread.start()
            self.status_thread.start()
            
            # Main loop to handle program termination
            while self.running:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                    break
                time.sleep(0.1)  # Reduce CPU usage
            
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        finally:
            # Stop all threads
            self.running = False
            
            # Release camera resources
            if self.posture_cap is not None:
                self.posture_cap.release()
            if self.eye_cap is not None:
                self.eye_cap.release()
            
            # Close all windows and cleanup
            cv2.destroyAllWindows()
            self.posture_detector.pose.close()
            
            # Wait briefly for threads to clean up
            time.sleep(1)
            
            print("\n✅ System closed successfully")
            
            # Save session data
            self.posture_detector.save_session_data()
            
            # Display final statistics
            print("\n=== Final Session Statistics ===")
            eye_stats = self.eye_monitor.get_statistics()
            print("\nEye Detection Stats:")
            for key, value in eye_stats.items():
                print(f"{key}: {value}")
            
            total_time = (self.posture_detector.good_posture_time + 
                         self.posture_detector.bad_posture_time +
                         self.posture_detector.sleeping_time)
            
            if total_time > 0:
                print("\nPosture Detection Stats:")
                print(f"Total time: {total_time:.1f} seconds")
                print(f"Good posture: {self.posture_detector.good_posture_time:.1f}s " +
                      f"({(self.posture_detector.good_posture_time/total_time*100):.1f}%)")
                print(f"Bad posture: {self.posture_detector.bad_posture_time:.1f}s " +
                      f"({(self.posture_detector.bad_posture_time/total_time*100):.1f}%)")
                print(f"Sleeping time: {self.posture_detector.sleeping_time:.1f}s " +
                      f"({(self.posture_detector.sleeping_time/total_time*100):.1f}%)")


def main():
    try:
        # Import numpy here to avoid circular import
        global np
        import numpy as np
        
        # Create and run system
        system = IntegratedSystem()
        
        # Set higher priority for eye detection thread
        import psutil
        p = psutil.Process()
        p.nice(psutil.HIGH_PRIORITY_CLASS)
        
        # Run the system
        system.run()
        
    except KeyboardInterrupt:
        print("\n⚠️ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        # Make sure to cleanup OpenCV windows
        cv2.destroyAllWindows()
        # Wait a bit to ensure proper cleanup
        time.sleep(0.5)


if __name__ == "__main__":
    main()