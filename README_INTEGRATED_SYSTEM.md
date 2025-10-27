# Integrated AI English Speaking Interactive Training System

## Overview
This system combines **Posture Detection** and **Eye Detection** running in parallel threads to monitor student engagement during online learning sessions.

## Architecture

### Main Components

1. **`main.py`** - The integrated system that runs both detection systems simultaneously
2. **`openpose/posture_detection.py`** - Posture detection using MediaPipe
3. **`eye_cnn/eye_detection_interface.py`** - Eye state detection using CNN model

## How It Works

### Parallel Thread Execution

The system creates **3 parallel threads**:

1. **Posture Detection Thread** (`run_posture_detection`)
   - Opens camera (VideoCapture 0)
   - Processes frames using MediaPipe Pose
   - Detects: GOOD_POSTURE, BAD_POSTURE, SLEEPING, NOT_VISIBLE
   - Displays output in "Posture Detection" window

2. **Eye Detection Thread** (`run_eye_detection`)
   - Opens camera (VideoCapture 0)
   - Processes frames using CNN model
   - Detects: ATTENTIVE, DROWSY, SLEEPING, DISTRACTED
   - Displays output in "Eye Detection" window

3. **Status Display Thread** (`display_status`)
   - Shows combined status from both systems
   - Displays real-time alerts and statistics
   - Shows in "System Status" window

### Thread Safety

- Uses `threading.Lock()` to protect shared state variables
- Ensures thread-safe updates to `eye_state` and `posture_state`
- Prevents race conditions when multiple threads access shared data

### Key Features

✅ **Real-time parallel processing** - Both systems run simultaneously
✅ **Thread-safe state management** - No data corruption
✅ **Multiple camera windows** - Separate displays for each detection system
✅ **Combined status dashboard** - Unified view of student engagement
✅ **Performance monitoring** - FPS counter and statistics
✅ **Session data logging** - Saves session statistics to JSON

## Running the System

### Prerequisites

```bash
pip install opencv-python mediapipe tensorflow numpy
```

### Execute

```bash
python main.py
```

### Controls

- Press **'q'** in any window to quit the system
- All windows will close gracefully
- Session statistics will be saved automatically

## Output Windows

1. **Posture Detection** (Left)
   - Shows skeleton overlay
   - Displays posture angles
   - Shows FPS counter

2. **Eye Detection** (Right)
   - Shows face detection
   - Displays eye state
   - Shows closed eyes counter

3. **System Status** (Center)
   - Combined status from both systems
   - Real-time alerts
   - Session statistics
   - Engagement percentages

## State Detection

### Posture States
- `GOOD_POSTURE` - Proper sitting posture
- `BAD_POSTURE` - Slouching or poor posture
- `SLEEPING` - Head down, possibly sleeping
- `NOT_VISIBLE` - Person not in frame

### Eye States
- `ATTENTIVE` - Eyes open, focused
- `DROWSY` - Eyes closing frequently
- `SLEEPING` - Eyes closed for extended period
- `DISTRACTED` - No face detected

## Technical Implementation

### Thread Creation
```python
self.posture_thread = threading.Thread(target=self.run_posture_detection)
self.eye_thread = threading.Thread(target=self.run_eye_detection)
self.status_thread = threading.Thread(target=self.display_status)
```

### Thread Safety
```python
with self.lock:
    self.eye_state = state['state']
    self.posture_state = "GOOD POSTURE" if is_good_posture else "BAD POSTURE"
```

### Graceful Shutdown
- All threads are set as daemon threads
- Camera resources are properly released
- OpenCV windows are destroyed
- Session data is saved before exit

## Session Data

Statistics are saved to JSON files:
- `posture_session_YYYYMMDD_HHMMSS.json`

Includes:
- Good posture percentage
- Bad posture percentage
- Sleeping time
- Total session duration
- Timestamps

## Benefits

🎯 **Comprehensive Monitoring** - Tracks both posture and attention
🔄 **Parallel Processing** - No performance bottleneck
📊 **Detailed Analytics** - Complete session statistics
⚡ **Real-time Feedback** - Immediate alerts for issues
💾 **Data Persistence** - Session history for analysis

## Troubleshooting

### Camera Access Issues
- Only one camera instance can be accessed at a time
- The system uses the same camera (index 0) for both threads
- If you get camera errors, ensure no other application is using the camera

### Performance Issues
- Reduce frame resolution if FPS is low
- Close unnecessary background applications
- Ensure good lighting for better detection accuracy

### Model Not Found
- Ensure `eye_detection_model.keras` exists in `eye_cnn/model/`
- Check the model path in the code

## Future Enhancements

- [ ] Use separate cameras for each detection system
- [ ] Add audio alerts for critical states
- [ ] Implement cloud-based session storage
- [ ] Add machine learning for behavior prediction
- [ ] Create web dashboard for remote monitoring

---

**Author**: AI English Speaking Training System
**Version**: 1.0
**Last Updated**: October 2025
