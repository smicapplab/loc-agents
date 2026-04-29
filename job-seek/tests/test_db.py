import pytest
import os
import asyncio
import pytest_asyncio
from src.utils.db import init_db, job_exists, save_job, DB_PATH

@pytest_asyncio.fixture(autouse=True, loop_scope="function")
async def setup_db():
    """Ensures a clean database for each test."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    await init_db()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

@pytest.mark.asyncio(loop_scope="function")
async def test_init_db():
    """Test that the database and table are created."""
    assert os.path.exists(DB_PATH)

@pytest.mark.asyncio(loop_scope="function")
async def test_save_and_exists():
    """Test saving a job and checking its existence."""
    job_id = "test-job-1"
    job_data = {
        "id": job_id,
        "title": "Software Engineer",
        "company": "Tech Corp",
        "link": "https://example.com/job",
        "posted_date": "2026-04-29",
        "date_emailed": "2026-04-29",
        "raw_desc": "Exciting role!"
    }
    
    # Initially should not exist
    assert await job_exists(job_id) is False
    
    # Save job
    await save_job(job_data)
    
    # Now should exist
    assert await job_exists(job_id) is True

@pytest.mark.asyncio(loop_scope="function")
async def test_job_not_exists():
    """Test checking existence of a non-existent job."""
    assert await job_exists("non-existent") is False
