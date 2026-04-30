import typer
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.core.gmail_api import GmailClient
from src.core.emailer import send_job_email
from logic import extract_jobs_from_html, filter_by_salary, review_filtered_jobs
import json

# Load environment variables from the root .env
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
load_dotenv(os.path.join(root_dir, ".env"))

app = typer.Typer(help="Job-Filter Agent CLI")

async def process_emails():
    """
    Fetches job alert emails, filters them, and scores them.
    """
    typer.echo("Initializing Gmail Client...")
    client = GmailClient()
    if not client.service:
        typer.secho("Error: Gmail Client could not be initialized. Check credentials.", fg=typer.colors.RED)
        return

    # 1. Determine Search Query (last 2 days, excluding already processed)
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime('%Y/%m/%d')
    query = f"from:(linkedin.com OR indeed.com OR jobstreet.com) after:{two_days_ago} -label:Jobs"
    typer.echo(f"Searching for emails with query: {query}")

    # 2. Search Messages
    messages = client.search_messages(query=query)
    typer.echo(f"Found {len(messages)} matching emails.")

    if not messages:
        return

    # 3. Load Profile
    profile_md_path = "data/profile.md"
    if not os.path.exists(profile_md_path):
        typer.secho(f"Error: Profile not found at {profile_md_path}", fg=typer.colors.RED)
        return
        
    with open(profile_md_path, "r") as f:
        profile_md = f.read()

    # Get label IDs
    jobs_label_id = client.get_or_create_label("Jobs")
    updates_label_id = "CATEGORY_UPDATES" # Built-in category Updates

    all_high_scored_jobs = []

    for msg in messages:
        msg_id = msg['id']
        typer.echo(f"Processing message {msg_id}...")
        
        # 4. Get Body and Extract Jobs
        html_body = client.get_message_body(msg_id)
        if not html_body:
            continue
            
        jobs = extract_jobs_from_html(html_body)
        typer.echo(f"  Extracted {len(jobs)} jobs from email.")

        # 5. Filter by Salary
        filtered_jobs = [j for j in jobs if filter_by_salary(j)]
        typer.echo(f"  {len(filtered_jobs)} jobs passed salary filter.")

        if not filtered_jobs:
            continue

        # 6. Review & Score
        scored_jobs = await review_filtered_jobs(filtered_jobs, profile_md)
        typer.echo(f"  {len(scored_jobs)} jobs matched profile (score >= 7).")

        if scored_jobs:
            all_high_scored_jobs.extend(scored_jobs)
            # 7. Modify Labels (Move to Jobs)
            client.modify_labels(msg_id, add_labels=[jobs_label_id], remove_labels=[updates_label_id, 'INBOX'])

    # 8. Send Summary Email
    if all_high_scored_jobs:
        typer.secho(f"\nFound {len(all_high_scored_jobs)} total matches!", fg=typer.colors.GREEN, bold=True)
        subject = f"JobFilter: {len(all_high_scored_jobs[:10])} matching alerts in your Gmail"
        send_job_email(all_high_scored_jobs[:10], subject=subject)
    else:
        typer.echo("\nNo high-scoring matches found today.")

@app.command()
def process():
    """
    Runs the full job-filter process.
    """
    asyncio.run(process_emails())

if __name__ == "__main__":
    app()
