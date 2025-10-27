import pyaudio
import numpy as np
import time
from datetime import datetime
from transformers import pipeline
import scipy.io.wavfile as wavfile
import mysql.connector
import json
import re
import sys

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",  
    database="speech_qaa"
)
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT * FROM questions")
questions = cursor.fetchall()
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny",
    generate_kwargs={"task": "transcribe", "language": "en"}
)

grammar_check = pipeline("text-classification", model="textattack/roberta-base-CoLA")

def evaluate_grammar_fluency(text):
    """Evaluate grammar quality using CoLA model"""
    try:
        result = grammar_check(text)[0]
        if result["label"] == "LABEL_1":
            return round(result["score"] * 100, 2)
        else:
            return round((1 - result["score"]) * 100, 2)
    except Exception as e:
        print("⚠ Grammar model error:", e)
        return 0.0

RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
BUFFER_DURATION = 6
BUFFER_SIZE = int(RATE * BUFFER_DURATION)

def normalize(text):
    return re.sub(r'[^\w\s]', '', text.lower())

def calculate_keyword_score(answer_text, keywords_json):
    """Compare answer text with target keywords"""
    keywords = json.loads(keywords_json)
    words = normalize(answer_text).split()
    matched = sum(1 for k in keywords if k.lower() in words)
    score = round((matched / len(keywords)) * 100, 2)
    return score, matched, len(keywords)

def ask_and_evaluate(question_obj, stream, user_name="Srinidhi"):
    print("\n============================================================")
    print(f"🗣  Question: {question_obj['question']}")
    print("------------------------------------------------------------")

    print("🎧 Get ready to answer in...")
    for i in range(3, 0, -1):
        print(f"👉 {i}")
        time.sleep(1)
    print("🎙 Start speaking now! (You have ~6 seconds)")

    audio_buffer = []
    start_time = time.time()
    max_duration = 20  
    silence_threshold = 0.01
    silence_duration = 3.0
    silence_start = None

    while True:
        audio_chunk = stream.read(CHUNK, exception_on_overflow=False)
        audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        audio_buffer.extend(audio_np)

        if np.abs(audio_np).mean() < silence_threshold:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start >= silence_duration:
                print("🔇 Silence detected. Recording stopped.")
                break
        else:
            silence_start = None

        if time.time() - start_time >= max_duration:
            print("⏳ Time's up! Stopping...")
            break

    segment = np.array(audio_buffer)
    rms = np.sqrt(np.mean(segment**2))
    if rms < silence_threshold:
        print("⚠ No meaningful audio detected. Skipping question.")
        return 0

    wavfile.write("answer.wav", RATE, np.int16(segment * 32767))
    print("⏳ Transcribing your answer...")
    result = asr(segment)
    answer_text = result["text"]
    print(f"📝 You said: {answer_text}")

    keyword_score, matched, total_keywords = calculate_keyword_score(answer_text, question_obj["keywords"])
    print(f"✅ Matched {matched}/{total_keywords} keywords | Keyword Score: {keyword_score}%")

    fluency_score = evaluate_grammar_fluency(answer_text)
    print(f"🧮 Grammar & Fluency Score: {fluency_score}%")

    weight = float(question_obj.get("weight", 0.2))
    total_score = round(weight * ((keyword_score * 0.7) + (fluency_score * 0.3)), 2)

    print("\n📊 ====== RESULTS ======")
    print(f"🗝 Keyword Score       : {keyword_score}%")
    print(f"🧠 Grammar/Fluency     : {fluency_score}%")
    print(f"⚖ Clip Weight (gᵢ)     : {weight}")
    print(f"🏁 Weighted Total Score : {total_score}%")
    print("===========================")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_query = """
        INSERT INTO responses 
        (question_id, response, matched_keywords, score, fluency_score, total_score, clip_weight, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        question_obj["id"], answer_text, matched,
        keyword_score, fluency_score, total_score, weight, timestamp
    ))
    db.commit()
    print("💾 Saved to MySQL successfully!\n")

    return total_score

try:
    print("🎙 Starting AIESIT English Speaking Practice\n")
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

    session_score = 0
    user_name = "Srinidhi"

    for q in questions:
        try:
            clip_score = ask_and_evaluate(q, stream, user_name)
            session_score += clip_score
            print("\nPress ENTER to continue or type 'exit' to stop:")
            user_input = input().strip().lower()
            if user_input == "exit":
                print("👋 Exiting by user choice.")
                break
        except KeyboardInterrupt:
            print("\n🛑 Skipped question safely.")
            continue

    print("\n📘 FINAL SESSION REPORT")
    print(f"🧮 Overall Weighted Score (Σ gᵢ × Sᵢ): {round(session_score, 2)}%")

    threshold = 60
    if session_score >= threshold:
        print("✅ Passed threshold — proceed to next level/video.")
    else:
        print("⚠ Below threshold — system suggests level downgrade.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO session_results (user_name, total_score, timestamp) VALUES (%s, %s, %s)",
        (user_name, session_score, timestamp)
    )
    db.commit()
    print("💾 Session summary saved to MySQL.")

except KeyboardInterrupt:
    print("\n👋 Session ended by user.")

finally:
    try:
        stream.stop_stream()
        stream.close()
    except:
        pass
    p.terminate()
    db.close()