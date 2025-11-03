"""
Test script to check the structure of questions from database
"""
from lecture_gui.database import db
import json

# Get a lecture from database
lecture = db.get_lecture_by_id(3)

print("=" * 60)
print("Lecture structure from database:")
print("=" * 60)
print(json.dumps(lecture, indent=2, default=str))

print("\n" + "=" * 60)
print("Questions structure:")
print("=" * 60)
if lecture and 'questions' in lecture:
    for q in lecture['questions']:
        print(f"\nQuestion {q.get('question_id', q.get('id'))}:")
        print(f"  Fields: {list(q.keys())}")
        print(f"  Text: {q.get('question_text', q.get('question', 'N/A'))[:50]}...")
        print(f"  Keywords: {q.get('keywords', [])}")
