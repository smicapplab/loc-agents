# Design Spec: OpenAI Support & Project Consistency

## 1. Goal
Add OpenAI support to both `job-seek` and `job-filter` projects and ensure naming consistency by using `kebab-case` for all project directories and updating shared logic.

## 2. Project Consistency
- Rename `job_filter` directory to `job-filter`.
- Ensure `job-seek` and `job-filter` are consistent in their structure.
- Update any hardcoded paths in the codebase that refer to the old directory names.

## 3. OpenAI Support
### 3.1. Configuration
Update `.env` files (and `.env.example`) to include:
- `AI_PROVIDER`: `gemini` (default) or `openai`
- `OPENAI_API_KEY`: Required if `AI_PROVIDER=openai`
- `OPENAI_MODEL`: Optional, default to `gpt-4o` or `gpt-3.5-turbo`
- `GEMINI_MODEL`: Optional, default to `gemini-2.0-flash`

### 3.2. Implementation Strategy (Inline Abstraction)
We will implement a lightweight abstraction in the following files to support both providers:
- `src/core/reviewer.py`: Used for scoring jobs.
- `src/utils/pdf_processor.py`: Used for structuring resumes.
- `job-filter/logic.py`: Used for extracting jobs from HTML.

#### Logic Flow:
1. Check `AI_PROVIDER` from environment.
2. If `openai`:
   - Initialize `openai.OpenAI` client.
   - Use `client.chat.completions.create` with appropriate parameters.
3. If `gemini`:
   - Use existing `google.generativeai` logic.

## 4. Proposed Changes
### 4.1. Directory Structure
- `job_filter/` -> `job-filter/`
- `job-seek/` (remains same)

### 4.2. Dependencies
Add `openai` to `job-seek/requirements.txt` and any other relevant requirements files.

### 4.3. Code Updates
- **Reviewer Class (`src/core/reviewer.py`)**: Update `__init__` to handle both clients and `review_job` to use the selected client.
- **PDF Processor (`src/utils/pdf_processor.py`)**: Update `structure_resume` to support OpenAI.
- **Job Filter Logic (`job-filter/logic.py`)**: Update `extract_jobs_from_html` and `review_filtered_jobs` to support OpenAI.

## 5. Success Criteria
- Running `job-seek` with `AI_PROVIDER=openai` successfully structures a resume and reviews jobs.
- Running `job-filter` with `AI_PROVIDER=openai` successfully extracts and scores jobs from emails.
- Project naming is consistent (`job-seek` and `job-filter`).
