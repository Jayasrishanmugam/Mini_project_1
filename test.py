# Model Evaluation Script - Calculate All Metrics
# Run this after training your model OR load a saved model

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
    mean_absolute_error
)

# ===== CONFIGURATION =====
MODEL_PATH = 'C:/Users/Aravindan/CNN_MODEL/model/eye_detection_model.keras'  # Your trained model path
TEST_DIR = 'C:/Users/Aravindan/Downloads/dataset/data/test'  # Or test folder
IMG_HEIGHT = 128
IMG_WIDTH = 128
BATCH_SIZE = 32

# ===== LOAD MODEL =====
print("Loading model...")
try:
    model = keras.models.load_model(MODEL_PATH)
    print("✅ Model loaded successfully!")
except:
    model = keras.models.load_model(MODEL_PATH, compile=False)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    print("✅ Model loaded with compile=False")

# ===== LOAD TEST DATA =====
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False  # Important! Don't shuffle for evaluation
)

print(f"\nFound {test_generator.samples} test images")
print(f"Classes: {test_generator.class_indices}")

# ===== GET PREDICTIONS =====
print("\nGenerating predictions...")
y_pred_probs = model.predict(test_generator, verbose=1)
y_pred = (y_pred_probs > 0.5).astype(int).flatten()
y_true = test_generator.classes

# ===== CALCULATE METRICS =====
print("\n" + "="*50)
print("📊 MODEL EVALUATION METRICS")
print("="*50)

# 1. ACCURACY
accuracy = accuracy_score(y_true, y_pred)
print(f"\n✅ Accuracy: {accuracy*100:.2f}%")

# 2. PRECISION
precision = precision_score(y_true, y_pred, average='binary')
print(f"✅ Precision: {precision*100:.2f}%")

# 3. RECALL (Sensitivity)
recall = recall_score(y_true, y_pred, average='binary')
print(f"✅ Recall: {recall*100:.2f}%")

# 4. F1-SCORE
f1 = f1_score(y_true, y_pred, average='binary')
print(f"✅ F1-Score: {f1*100:.2f}%")

# 5. MEAN ABSOLUTE ERROR
mae = mean_absolute_error(y_true, y_pred)
print(f"✅ MAE: {mae:.4f}")

# 6. CONFUSION MATRIX
cm = confusion_matrix(y_true, y_pred)
print("\n📊 Confusion Matrix:")
print(cm)

# Get class names
class_names = list(test_generator.class_indices.keys())
print(f"\nClass 0: {class_names[0]}")
print(f"Class 1: {class_names[1]}")

# Calculate from confusion matrix
tn, fp, fn, tp = cm.ravel()
print(f"\nTrue Negatives: {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"True Positives: {tp}")

# 7. CLASSIFICATION REPORT
print("\n" + "="*50)
print("📋 DETAILED CLASSIFICATION REPORT")
print("="*50)
print(classification_report(y_true, y_pred, target_names=class_names))

# ===== VISUALIZATIONS =====

# 1. CONFUSION MATRIX HEATMAP
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names, 
            yticklabels=class_names,
            cbar=True)
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')

# 2. METRICS BAR CHART
plt.subplot(1, 3, 2)
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
scores = [accuracy, precision, recall, f1]
colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
bars = plt.bar(metrics, scores, color=colors, alpha=0.7, edgecolor='black')
plt.ylim(0, 1)
plt.ylabel('Score')
plt.title('Model Performance Metrics', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height*100:.1f}%',
             ha='center', va='bottom', fontweight='bold')

# 3. ROC CURVE
plt.subplot(1, 3, 3)
fpr, tpr, thresholds = roc_curve(y_true, y_pred_probs)
roc_auc = auc(fpr, tpr)

plt.plot(fpr, tpr, color='darkorange', lw=2, 
         label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
         label='Random Classifier')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve', fontsize=14, fontweight='bold')
plt.legend(loc="lower right")
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('model_evaluation_metrics.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n✅ Visualization saved as 'model_evaluation_metrics.png'")

# ===== PREDICTION DISTRIBUTION =====
plt.figure(figsize=(12, 4))

# Prediction probability distribution
plt.subplot(1, 2, 1)
plt.hist(y_pred_probs[y_true == 0], bins=30, alpha=0.7, 
         label=f'{class_names[0]} (Actual)', color='blue')
plt.hist(y_pred_probs[y_true == 1], bins=30, alpha=0.7, 
         label=f'{class_names[1]} (Actual)', color='red')
plt.xlabel('Prediction Probability')
plt.ylabel('Frequency')
plt.title('Prediction Probability Distribution', fontweight='bold')
plt.legend()
plt.grid(alpha=0.3)

# Correct vs Incorrect predictions
plt.subplot(1, 2, 2)
correct = (y_pred == y_true).sum()
incorrect = (y_pred != y_true).sum()
labels = ['Correct', 'Incorrect']
sizes = [correct, incorrect]
colors = ['#2ecc71', '#e74c3c']
explode = (0.1, 0)

plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
plt.title('Prediction Accuracy Distribution', fontweight='bold')

plt.tight_layout()
plt.savefig('prediction_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Distribution plot saved as 'prediction_distribution.png'")

# ===== SAVE METRICS TO FILE =====
with open('model_metrics.txt', 'w') as f:
    f.write("="*50 + "\n")
    f.write("MODEL EVALUATION METRICS\n")
    f.write("="*50 + "\n\n")
    f.write(f"Accuracy: {accuracy*100:.2f}%\n")
    f.write(f"Precision: {precision*100:.2f}%\n")
    f.write(f"Recall: {recall*100:.2f}%\n")
    f.write(f"F1-Score: {f1*100:.2f}%\n")
    f.write(f"MAE: {mae:.4f}\n")
    f.write(f"AUC-ROC: {roc_auc:.4f}\n\n")
    f.write("Confusion Matrix:\n")
    f.write(str(cm) + "\n\n")
    f.write("Classification Report:\n")
    f.write(classification_report(y_true, y_pred, target_names=class_names))

print("\n✅ Metrics saved to 'model_metrics.txt'")

# ===== SUMMARY =====
print("\n" + "="*50)
print("📊 SUMMARY")
print("="*50)
print(f"Total Test Images: {len(y_true)}")
print(f"Correctly Classified: {correct} ({correct/len(y_true)*100:.1f}%)")
print(f"Incorrectly Classified: {incorrect} ({incorrect/len(y_true)*100:.1f}%)")
print(f"\nBest Metric: F1-Score = {f1*100:.2f}%")
print(f"Model Quality: {'Excellent' if f1 > 0.9 else 'Good' if f1 > 0.8 else 'Fair' if f1 > 0.7 else 'Needs Improvement'}")
print("="*50)

print("\n✅ Evaluation Complete!")