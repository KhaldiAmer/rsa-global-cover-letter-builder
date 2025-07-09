import os
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from typing import Optional, List
from urllib.parse import urlparse
from .application import JobApplication

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/jobtracker"
)


class Database:
    def __init__(self):
        self.conn = None

    def connect(self, max_retries=3, retry_delay=2):
        """Connect to database with retry logic"""
        for attempt in range(max_retries):
            try:
                # Parse the DATABASE_URL to handle SSL properly
                parsed_url = urlparse(DATABASE_URL)

                print(
                    f"Attempting to connect to database at {parsed_url.hostname}:{parsed_url.port}"
                )

                # For Render PostgreSQL, try direct connection first
                if "render.com" in parsed_url.hostname:
                    print("Detected Render PostgreSQL, trying direct connection...")
                    try:
                        # Try connecting directly with the URL first
                        self.conn = psycopg2.connect(DATABASE_URL)
                        self.conn.set_session(autocommit=False)
                        print(
                            f"Successfully connected to Render PostgreSQL using direct URL"
                        )
                        return
                    except psycopg2.OperationalError as direct_error:
                        print(f"Direct connection failed: {direct_error}")
                        print("Trying with explicit SSL parameters...")

                # Extract connection parameters
                db_params = {
                    "host": parsed_url.hostname,
                    "port": parsed_url.port or 5432,
                    "database": parsed_url.path[1:],  # Remove leading slash
                    "user": parsed_url.username,
                    "password": parsed_url.password,
                }

                # Add SSL parameters for Render PostgreSQL
                if "render.com" in parsed_url.hostname:
                    print("Configuring SSL parameters for Render...")
                    db_params.update(
                        {
                            "sslmode": "require",
                            "sslcert": None,
                            "sslkey": None,
                            "sslrootcert": None,
                        }
                    )
                    print(f"SSL parameters: sslmode={db_params.get('sslmode')}")

                print(
                    f"Connection parameters: host={db_params['host']}, port={db_params['port']}, database={db_params['database']}, user={db_params['user']}"
                )

                self.conn = psycopg2.connect(**db_params)
                self.conn.set_session(autocommit=False)
                print(f"Successfully connected to database at {parsed_url.hostname}")
                return

            except psycopg2.OperationalError as e:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print("Max retries reached. Database connection failed.")
                    raise
            except Exception as e:
                print(f"Unexpected error during database connection: {e}")
                print(f"Error type: {type(e).__name__}")
                raise

    def close(self):
        if self.conn:
            self.conn.close()

    def is_connected(self):
        """Check if database connection is still valid"""
        try:
            if self.conn is None:
                return False
            # Try a simple query to test the connection
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return True
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            return False

    def ensure_connected(self):
        """Ensure database connection is valid, reconnect if needed"""
        if not self.is_connected():
            print("Database connection lost, attempting to reconnect...")
            self.connect()


db = Database()


def init_db():
    try:
        db.connect()
        with db.conn.cursor() as cur:
            cur.execute(
                """
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
            """
            )
            db.conn.commit()
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise


def get_db():
    return db


def save_application(db: Database, application: JobApplication):
    db.ensure_connected()
    with db.conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO applications (id, company, role, job_description, resume, user_email, deadline_duration, created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                application.id,
                application.company,
                application.role,
                application.job_description,
                application.resume,
                application.user_email,
                application.deadline_duration,
                application.created_at,
                application.status.value,
            ),
        )
        db.conn.commit()


def get_application(db: Database, application_id: str) -> Optional[JobApplication]:
    db.ensure_connected()
    with db.conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM applications WHERE id = %s", (application_id,))
        row = cur.fetchone()
        if row:
            return JobApplication(
                id=row["id"],
                company=row["company"],
                role=row["role"],
                job_description=row["job_description"],
                resume=row["resume"],
                user_email=row["user_email"],
                deadline_duration=row["deadline_duration"],
                created_at=row["created_at"],
                status=row["status"],
            )
        return None


def get_all_applications(db: Database) -> List[JobApplication]:
    db.ensure_connected()
    with db.conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM applications ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [
            JobApplication(
                id=row["id"],
                company=row["company"],
                role=row["role"],
                job_description=row["job_description"],
                resume=row["resume"],
                user_email=row["user_email"],
                deadline_duration=row["deadline_duration"],
                created_at=row["created_at"],
                status=row["status"],
            )
            for row in rows
        ]
