# Eye Open/Closed Detection using CNN
# Google Colab Implementation

# ===== STEP 1: UPLOAD DATASET TO COLAB =====
# Option A: Upload from local computer (for small datasets)
from google.colab import files
import zipfile
import os

# Uncomment to upload a zip file containing your dataset
# uploaded = files.upload()
# 
# # Extract the uploaded zip file
# for filename in uploaded.keys():
#     with zipfile.ZipFile(filename, 'r') as zip_ref:
#         zip_ref.extractall('/content/dataset')

# Option B: Mount Google Drive (recommended for larger datasets)
from google.colab import drive
drive.mount('/content/drive')


import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import numpy as np

# ===== STEP 3: SET PARAMETERS =====
IMG_HEIGHT = 128
IMG_WIDTH = 128
BATCH_SIZE = 32
EPOCHS = 20

# Update these paths according to your dataset location
TRAIN_DIR = '/content/dataset/train'  # Change this to your path
VAL_DIR = '/content/dataset/validation'  # Change this to your path

# ===== STEP 4: DATA PREPROCESSING & AUGMENTATION =====
# Training data with augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Validation data (only rescaling)
val_datagen = ImageDataGenerator(rescale=1./255)

# Load training data
train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary',  # binary for 2 classes
    shuffle=True
)

# Load validation data
val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False
)

print(f"Found {train_generator.samples} training images")
print(f"Found {val_generator.samples} validation images")
print(f"Class indices: {train_generator.class_indices}")

# ===== STEP 5: BUILD CNN MODEL =====
model = keras.Sequential([
    # First Convolutional Block
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    
    # Second Convolutional Block
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    
    # Third Convolutional Block
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    
    # Fourth Convolutional Block
    layers.Conv2D(256, (3, 3), activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),
    
    # Flatten and Dense Layers
    layers.Flatten(),
    layers.Dropout(0.5),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')  # Binary classification
])

# ===== STEP 6: COMPILE MODEL =====
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Display model architecture
model.summary()

# ===== STEP 7: TRAIN THE MODEL =====
# Add callbacks for better training
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

reduce_lr = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=3,
    min_lr=1e-7
)

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=[early_stopping, reduce_lr]
)

# ===== STEP 8: VISUALIZE TRAINING RESULTS =====
plt.figure(figsize=(12, 4))

# Plot accuracy
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

# Plot loss
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# ===== STEP 9: EVALUATE MODEL =====
val_loss, val_accuracy = model.evaluate(val_generator)
print(f"\nValidation Accuracy: {val_accuracy*100:.2f}%")
print(f"Validation Loss: {val_loss:.4f}")

# ===== STEP 10: SAVE THE MODEL =====
# Save in Keras format
model.save('/content/eye_detection_model.keras')
print("Model saved as 'eye_detection_model.keras'")

# Save to Google Drive (if mounted)
# model.save('/content/drive/MyDrive/eye_detection_model.keras')

# ===== STEP 11: PREDICT ON NEW IMAGES =====
# def predict_eye_state(image_path):
#     """Predict if eyes are open or closed"""
#     img = keras.preprocessing.image.load_img(
#         image_path, 
#         target_size=(IMG_HEIGHT, IMG_WIDTH)
#     )
#     img_array = keras.preprocessing.image.img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0) / 255.0
    
#     prediction = model.predict(img_array)[0][0]
    
#     # Assuming: 0 = closed, 1 = open (check your class_indices)
#     if prediction > 0.5:
#         return "Eyes Open", prediction
#     else:
#         return "Eyes Closed", prediction

# # Example usage:
# # result, confidence = predict_eye_state('/path/to/test/image.jpg')
# # print(f"Prediction: {result}, Confidence: {confidence:.4f}")

# print("\n✅ Training Complete! Model is ready to use.")