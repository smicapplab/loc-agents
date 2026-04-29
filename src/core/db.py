import aiosqlite
import os

DB_PATH = "data/jobs.db"

async def init_db():
    """Initializes the SQLite database and creates the jobs table if it doesn't exist."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                link TEXT,
                posted_date TEXT,
                date_emailed TEXT,
                raw_desc TEXT
            )
        """)
        await db.commit()

async def job_exists(job_id: str) -> bool:
    """Checks if a job already exists in the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None

async def save_job(job_data: dict):
    """Saves a new job to the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO jobs (id, title, company, link, posted_date, date_emailed, raw_desc) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_data.get('id'),
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('link'),
                job_data.get('posted_date'),
                job_data.get('date_emailed'),
                job_data.get('raw_desc')
            )
        )
        await db.commit()

async def get_all_jobs():
    """Retrieves all jobs from the database (mainly for debugging/UI)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM jobs") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
