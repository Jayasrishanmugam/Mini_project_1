# Quick Start Guide - Integrated System

## 🚀 Running the Integrated System

### Step 1: Install Dependencies
```bash
pip install opencv-python mediapipe tensorflow numpy psutil
```

### Step 2: Run the Main Program
```bash
python main.py
```

### Step 3: What to Expect

The system will open **3 windows**:

1. **Posture Detection** (Left side)
   - Shows your body skeleton
   - Green = Good posture
   - Red = Bad posture
   
2. **Eye Detection** (Right side)
   - Shows your face with eye regions
   - Tracks if you're attentive or drowsy
   
3. **System Status** (Center)
   - Combined dashboard
   - Real-time alerts
   - Session statistics

### Step 4: Exit the Program
- Press **'q'** in any window
- System will save session data
- All windows close automatically

## 📊 Understanding the Output

### Posture States
| State | Meaning | Color |
|-------|---------|-------|
| GOOD_POSTURE | Sitting upright | Green |
| BAD_POSTURE | Slouching | Yellow/Red |
| SLEEPING | Head down | Red |
| NOT_VISIBLE | Not in frame | Orange |

### Eye States
| State | Meaning | Color |
|-------|---------|-------|
| ATTENTIVE | Eyes open, focused | Green |
| DROWSY | Eyes closing | Yellow |
| SLEEPING | Eyes closed long | Red |
| DISTRACTED | Face not detected | Orange |

## 🎯 How the Parallel Threading Works

```
Main Program (main.py)
    │
    ├─── Thread 1: Posture Detection
    │    └─── Runs continuously
    │         Processes camera frames
    │         Updates posture_state
    │
    ├─── Thread 2: Eye Detection
    │    └─── Runs continuously
    │         Processes camera frames
    │         Updates eye_state
    │
    └─── Thread 3: Status Display
         └─── Reads both states
              Shows combined status
              Displays alerts
```

## 🔧 Key Features

✅ **Both programs run simultaneously** - No waiting!
✅ **Real-time updates** - Instant feedback
✅ **Thread-safe** - No data conflicts
✅ **Automatic session logging** - Saves to JSON
✅ **Performance optimized** - Shows FPS

## 📁 Output Files

After running, you'll find:
- `posture_session_YYYYMMDD_HHMMSS.json` - Session statistics

## ⚠️ Troubleshooting

### Camera not opening?
- Close other apps using the camera (Zoom, Teams, etc.)
- Check camera permissions in Windows Settings

### Low FPS?
- Close background applications
- Reduce window size
- Ensure good lighting

### Model not found error?
- Check if `eye_cnn/model/eye_detection_model.keras` exists
- Verify the file path is correct

## 💡 Tips for Best Results

1. **Good Lighting** - Ensure your face is well-lit
2. **Stable Position** - Sit at a consistent distance from camera
3. **Clear Background** - Helps with detection accuracy
4. **Camera Quality** - Better camera = better detection

## 🎓 Use Cases

- **Online Learning** - Monitor student engagement
- **Remote Work** - Track posture during long sessions
- **Health Monitoring** - Detect drowsiness while studying
- **Productivity Tracking** - Analyze work habits

---

**Need Help?** Check the detailed README_INTEGRATED_SYSTEM.md
