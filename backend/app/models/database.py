import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List
from .application import JobApplication

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/jobtracker")

class Database:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.set_session(autocommit=False)
    
    def close(self):
        if self.conn:
            self.conn.close()

db = Database()

def init_db():
    try:
        db.connect()
        with db.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id VARCHAR PRIMARY KEY,
                    company VARCHAR NOT NULL,
                    role VARCHAR NOT NULL,
                    job_description TEXT NOT NULL,
                    resume TEXT NOT NULL,
                    user_email VARCHAR NOT NULL,
                    deadline_duration INTERVAL NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    status VARCHAR DEFAULT 'SUBMITTED'
                )
            """)
            db.conn.commit()
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

def get_db():
    return db

def save_application(db: Database, application: JobApplication):
    with db.conn.cursor() as cur:
        cur.execute("""
            INSERT INTO applications (id, company, role, job_description, resume, user_email, deadline_duration, created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            application.id, application.company, application.role, application.job_description,
            application.resume, application.user_email, application.deadline_duration,
            application.created_at, application.status.value
        ))
        db.conn.commit()

def get_application(db: Database, application_id: str) -> Optional[JobApplication]:
    with db.conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM applications WHERE id = %s", (application_id,))
        row = cur.fetchone()
        if row:
            return JobApplication(
                id=row['id'],
                company=row['company'],
                role=row['role'],
                job_description=row['job_description'],
                resume=row['resume'],
                user_email=row['user_email'],
                deadline_duration=row['deadline_duration'],
                created_at=row['created_at'],
                status=row['status']
            )
        return None

def get_all_applications(db: Database) -> List[JobApplication]:
    with db.conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM applications ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [JobApplication(
            id=row['id'],
            company=row['company'],
            role=row['role'],
            job_description=row['job_description'],
            resume=row['resume'],
            user_email=row['user_email'],
            deadline_duration=row['deadline_duration'],
            created_at=row['created_at'],
            status=row['status']
        ) for row in rows]