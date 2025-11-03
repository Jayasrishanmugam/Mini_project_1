# Database Migration Guide

## Overview
This project has been successfully migrated from JSON file storage to MySQL database for better data management, scalability, and performance.

## Database Schema

### Tables Structure

#### 1. **lectures**
Stores lecture information
```sql
- id (INT, PRIMARY KEY)
- title (VARCHAR)
- video_file (VARCHAR)
- duration (VARCHAR)
- created_at (TIMESTAMP)
```

#### 2. **questions**
Stores questions associated with lectures
```sql
- id (INT, PRIMARY KEY)
- lecture_id (INT, FOREIGN KEY)
- question_id (INT)
- question_text (TEXT)
- keywords (TEXT)
- weight (FLOAT)
- avatar_video (VARCHAR)
```

#### 3. **sessions**
Stores user session data
```sql
- id (INT, PRIMARY KEY)
- lecture_id (INT)
- lecture_title (VARCHAR)
- timestamp (DATETIME)
- total_questions (INT)
- answered (INT)
- session_score (FLOAT)
- passed (BOOLEAN)
- ai_feedback (TEXT)
- ai_generated (BOOLEAN)
- created_at (TIMESTAMP)
```

#### 4. **performance_metrics**
Stores detailed performance metrics for each session
```sql
- id (INT, PRIMARY KEY)
- session_id (INT, FOREIGN KEY)
- avg_fluency (FLOAT)
- avg_keyword_match (FLOAT)
- avg_words_per_answer (FLOAT)
- posture_confidence (FLOAT)
- posture_warnings (INT)
- sleeping_detected (INT)
```

#### 5. **session_questions**
Stores individual question results for each session
```sql
- id (INT, PRIMARY KEY)
- session_id (INT, FOREIGN KEY)
- question_id (INT)
- question_text (TEXT)
- keyword_score (FLOAT)
- fluency_score (FLOAT)
- total_score (FLOAT)
- matched_keywords (INT)
- total_keywords (INT)
- answer_text (TEXT)
- feedback (TEXT)
```

## Database Configuration

The database connection is configured in `lecture_gui/database.py`:

```python
DatabaseManager(
    host="localhost",
    user="root",
    password="12345",  # Change this to your MySQL password
    database="english_training"
)
```

## Migration Scripts

### Complete Migration
To migrate all data from JSON to MySQL:
```bash
python migrate_to_database.py
```

This will:
1. ✅ Migrate all lectures and questions from `config.json`
2. ✅ Migrate all session history from `session_summaries.json`
3. ✅ Verify the migration was successful

### Test Database Operations
To test that the database is working correctly:
```bash
python test_database_fetch.py
```

## API Usage

### Fetching Lectures

```python
from lecture_gui.database import db

# Get all lectures with questions
lectures = db.get_all_lectures()

# Get a specific lecture
lecture = db.get_lecture_by_id(3)
```

### Saving Session Data

```python
from lecture_gui.database import db

session_data = {
    'lecture_id': 3,
    'lecture_title': 'English Speaking Skills',
    'timestamp': '2025-10-29 21:30:00',
    'total_questions': 5,
    'answered': 5,
    'session_score': 85.5,
    'passed': True,
    'performance_metrics': {
        'avg_fluency': 80.0,
        'avg_keyword_match': 90.0,
        'avg_words_per_answer': 25.5,
        'posture_confidence': 85.0,
        'posture_warnings': 2,
        'sleeping_detected': 0
    },
    'ai_feedback': 'Great job!',
    'ai_generated': True,
    'results': [
        {
            'question_id': 1,
            'question': 'What is pronunciation?',
            'result': {
                'keyword_score': 80.0,
                'fluency_score': 85.0,
                'total_score': 82.5,
                'matched': 4,
                'total_keywords': 5,
                'answer_text': 'Pronunciation is...'
            },
            'feedback': 'Good answer!'
        }
    ]
}

db.save_session(session_data)
```

### Retrieving Session History

```python
from lecture_gui.database import db

# Get recent sessions
sessions = db.get_session_history(limit=10)

# Get specific session details
session = db.get_session_details(session_id=5)
```

## Benefits of MySQL Migration

### ✅ Improved Performance
- Faster data retrieval with indexed queries
- Efficient handling of large datasets
- Optimized storage and memory usage

### ✅ Better Data Management
- Structured data with defined relationships
- Data integrity with foreign key constraints
- Easier to query and analyze data

### ✅ Scalability
- Can handle millions of records
- Concurrent user access support
- Better resource management

### ✅ Data Security
- User authentication and permissions
- Data encryption support
- Backup and recovery options

### ✅ Advanced Features
- Complex queries with JOINs
- Aggregation and analytics
- Transaction support (ACID compliance)

## Code Changes

### lecture_player.py
Updated `load_config()` method to fetch lectures from database:
```python
def load_config(self):
    # Load basic config from JSON
    with open(config_path, 'r') as f:
        self.config = json.load(f)
    
    # Load lectures from database
    from .database import db
    lectures = db.get_all_lectures()
    
    if lectures:
        self.config['lectures'] = lectures
```

### question_session.py
Updated session saving methods to use database:
```python
def _save_session_summary_with_feedback(self, ...):
    summary = {...}
    success = db.save_session(summary)
```

## Maintenance

### Backup Database
```bash
mysqldump -u root -p english_training > backup.sql
```

### Restore Database
```bash
mysql -u root -p english_training < backup.sql
```

### View Database Tables
```sql
USE english_training;
SHOW TABLES;
SELECT COUNT(*) FROM lectures;
SELECT COUNT(*) FROM questions;
SELECT COUNT(*) FROM sessions;
```

## Troubleshooting

### Connection Issues
1. Ensure MySQL server is running
2. Check username and password in `database.py`
3. Verify database exists: `SHOW DATABASES;`

### Migration Issues
1. Check file paths in migration scripts
2. Verify JSON files exist and are valid
3. Review error messages for specific issues

### Application Issues
1. Ensure database connection is established
2. Check if tables are created properly
3. Verify data was migrated successfully

## Future Enhancements

- [ ] Add user authentication and profiles
- [ ] Implement data analytics dashboard
- [ ] Add export/import functionality
- [ ] Create API endpoints for mobile apps
- [ ] Add real-time progress tracking
- [ ] Implement caching for better performance

---

**Note**: Make sure to update the database password in `database.py` with your actual MySQL root password before running the application.
