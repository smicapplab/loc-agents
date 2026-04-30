import typer
import asyncio
import os
from dotenv import load_dotenv
from src.utils.pdf_processor import extract_text_from_pdf, structure_resume
from src.agents.graph import create_job_hunt_graph
from src.core.emailer import send_job_email
from src.core.db import save_job, init_db
import json

# Load environment variables from the root .env
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
load_dotenv(os.path.join(root_dir, ".env"))

app = typer.Typer(help="PH Job-Seek AI Agent CLI")

@app.command()
def sync(
    resume_path: str = typer.Option("data/resume.pdf", help="Path to the resume PDF file"),
    output_dir: str = typer.Option("data", help="Directory to save the generated profile files")
):
    """
    Synchronizes the resume PDF with the structured profile files (MD and JSON).
    """
    if not os.path.exists(resume_path):
        typer.secho(f"Error: Resume not found at {resume_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Processing resume: {resume_path}...")

    try:
        # 1. Extract text
        text = extract_text_from_pdf(resume_path)
        typer.echo("Text extracted successfully.")

        # 2. Structure with Gemini
        typer.echo("Consulting AI for structuring (this may take a moment)...")
        md_content, json_index = structure_resume(text)

        # 3. Save files
        os.makedirs(output_dir, exist_ok=True)
        
        md_path = os.path.join(output_dir, "profile.md")
        json_path = os.path.join(output_dir, "profile_index.json")

        with open(md_path, "w") as f:
            f.write(md_content)
        
        with open(json_path, "w") as f:
            f.write(json_index)

        typer.secho(f"Success! Profile saved to:", fg=typer.colors.GREEN)
        typer.echo(f" - {md_path}")
        typer.echo(f" - {json_path}")

    except Exception as e:
        typer.secho(f"Error during synchronization: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def search(
    keywords: str = typer.Option(None, help="Job keywords to search for. If not provided, will use titles from profile_index.json"),
    location: str = typer.Option("Philippines", help="Location to search for jobs"),
    limit: int = typer.Option(5, help="Number of top matches to display")
):
    """
    Runs the autonomous job hunt using LangGraph and sends an email report.
    """
    # 1. Load Profile
    profile_md_path = "data/profile.md"
    profile_json_path = "data/profile_index.json"
    
    if not os.path.exists(profile_md_path) or not os.path.exists(profile_json_path):
        typer.secho("Error: Profile files not found. Please run 'sync' first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    with open(profile_md_path, "r") as f:
        profile_md = f.read()
        
    with open(profile_json_path, "r") as f:
        profile_index = json.load(f)
        
    # 2. Determine Keywords
    if not keywords:
        titles = profile_index.get("target_job_titles", [])
        if titles:
            keywords = titles[0] # Use the first title as default
        else:
            keywords = "Software Engineer"
            
    typer.echo(f"Starting job hunt for '{keywords}' in {location}...")
    
    # 3. Initialize Graph
    graph = create_job_hunt_graph()
    
    # 4. Run Graph
    async def run_hunt():
        initial_state = {
            "keywords": keywords,
            "location": location,
            "profile_md": profile_md,
            "raw_jobs": [],
            "new_jobs": [],
            "scored_jobs": []
        }
        
        result = await graph.ainvoke(initial_state)
        return result

    result = asyncio.run(run_hunt())
    
    # 5. Display and Save Results
    scored_jobs = result.get("scored_jobs", [])
    
    if not scored_jobs:
        typer.echo("No new high-scoring matches found.")
        return
        
    typer.secho(f"\nFound {len(scored_jobs)} top matches:", fg=typer.colors.GREEN, bold=True)
    
    top_matches = scored_jobs[:limit]
    
    # Define an async function to handle DB operations
    async def process_jobs(jobs):
        await init_db()
        for job in jobs:
            await save_job(job)

    # Run the DB operations
    asyncio.run(process_jobs(top_matches))
    
    for job in top_matches:
        score = job.get('score', 0)
        color = typer.colors.GREEN if score >= 8 else typer.colors.YELLOW
        
        typer.echo("-" * 40)
        typer.secho(f"[{score}/10] {job.get('title')}", fg=color, bold=True)
        typer.echo(f"Company: {job.get('company')}")
        typer.echo(f"Link: {job.get('link')}")
        
        eval_data = job.get('evaluation', {})
        typer.echo(f"Reason: {eval_data.get('reasoning')}")
        if eval_data.get('match_highlights'):
            typer.echo(f"Highlights: {', '.join(eval_data.get('match_highlights'))}")

    # 6. Email Results (Always enabled)
    if scored_jobs:
        typer.echo("\nSending email report...")
        subject = f"JobBoard: Found {len(top_matches)} matches for {keywords}"
        send_job_email(top_matches, subject=subject)

if __name__ == "__main__":
    app()
