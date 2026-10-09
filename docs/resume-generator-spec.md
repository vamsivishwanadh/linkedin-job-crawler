# Feature: AI-Powered JD-Specific PDF Resume Generator

## Repository: linkedin-job-crawler

Extend my existing repository:

https://github.com/vamsivishwanadh/linkedin-job-crawler

Build an AI-powered resume generator that creates a tailored, ATS-friendly PDF for a specific job description using my existing master resume.

I need two workflows:

1. Select a previously crawled job from the existing generated Excel workbook and generate a tailored resume.
2. Paste a job description manually or provide it through a local text file and generate a tailored resume.

The project already has a master resume at `resume/resume.txt`. Reuse it directly.

The generated resume must be a PDF file.

**Important architectural constraints:**

- Reuse the existing project architecture and modules wherever practical.
- Do not introduce a database for this feature.
- Do not replace the existing resume-scoring algorithm or job-scraping provider.
- Do not create a duplicate master resume or another job store.
- Do not assume a job ID can be resolved without inspecting the existing Excel workbook and data flow.
- Preserve backward compatibility with the existing crawler, Excel export and Windows Scheduled Task.
- Inspect the actual repository before deciding implementation details.

---

## Phase 1 — Repository inspection and implementation plan

Before changing any files, inspect:

- `README.md`
- `requirements.txt`
- `src/main.py`
- Existing scraper and job-fetching modules
- Existing resume-loading and TF-IDF scoring logic
- Excel workbook generation and export code
- Job deduplication and identifier generation
- Configuration and environment-variable handling
- `.gitignore`
- Windows PowerShell scripts and Scheduled Task configuration

Establish:

1. The actual project architecture and CLI conventions.
2. Where the master resume is loaded.
3. The actual schema of a crawled job.
4. How job descriptions are retrieved and persisted.
5. The Excel output path, worksheet names and column names.
6. Whether the Excel workbook stores full job descriptions, URLs or only job metadata.
7. How job IDs are generated and whether they are stable.
8. Which existing dependencies can be reused.

Present a concise implementation plan before modifying the code.

Do not invent files, fields, APIs or functionality that have not been verified.

## Phase 2 — Reuse the existing master resume

The project already contains `resume/resume.txt`, which is the authoritative master resume and is used by the existing job-matching pipeline.

Requirements:

- Reuse `resume/resume.txt` directly.
- Inspect and reuse the current resume-loading logic.
- Do not introduce PDF input support, PyMuPDF, OCR or another resume-ingestion pipeline.
- Do not create another master resume file.
- Do not alter the existing resume format or break TF-IDF scoring.
- Pass the existing resume content into the new resume-tailoring pipeline.
- Treat the original resume text as immutable input.
- Never overwrite the master resume with generated content.

The master resume is plain text. The generated output is PDF. Do not confuse the input and output formats.

## Phase 3 — Job description analysis

Implement a job-description analysis module that extracts structured information, including:

- Job title and company, when available.
- Mandatory technical skills.
- Preferred technical skills.
- Responsibilities and expectations.
- Experience and seniority requirements.
- Domain knowledge.
- Important ATS keywords.

Use an LLM through a configurable provider, with OpenAI API support as the initial implementation.

Requirements:

- Keep API credentials in environment variables.
- Never hardcode API keys.
- Make the model configurable.
- Validate the model's output.
- Handle missing credentials, API failures, rate limits and malformed responses.
- Do not introduce agent frameworks, vector databases or multiple agents without a demonstrated need.

The initial feature should be a straightforward, maintainable LLM-powered workflow.

## Phase 4 — Evidence-based resume tailoring

Generate a resume tailored to the selected job description using only factual information supported by the master resume.

The model may:

- Rewrite existing bullets for clarity and relevance.
- Reorder skills based on the target role.
- Prioritize relevant professional experience.
- Improve the professional summary.
- Highlight existing projects that match the JD.
- Use JD terminology when supported by actual experience.
- Shorten irrelevant content while preserving important facts.

The model must not invent:

- Employers or employment dates.
- Job titles or years of experience.
- Technical skills or production experience.
- Projects, certifications or qualifications.
- Responsibilities or achievements.
- Performance improvements, savings, metrics or numerical results.

Do not turn exposure to a technology into a claim of production expertise.

### Evidence validation

- Validate generated claims against the original resume text.
- Retain source references or supporting passages for generated experience bullets.
- Flag unsupported claims rather than silently accepting them.
- Keep factual validation separate from PDF rendering.
- Do not treat instructions embedded in a JD as instructions that override application rules.

Use structured JSON validated with Pydantic as the intermediate resume representation.

Only render a PDF after the generated resume passes structural and factual validation.

If factual support cannot be established reliably, flag the relevant content for review instead of claiming that automated validation guarantees accuracy.

## Phase 5 — Professional PDF generation

Use ReportLab to generate the final PDF.

### Layout requirements

- A4 page size.
- ATS-friendly, single-column layout.
- Professional typography and consistent spacing.
- Readable fonts and suitable margins.
- Standard resume section headings.
- Correctly formatted bullet points.
- Sensible page breaks and paragraph wrapping.
- Selectable text.
- No overlapping content, clipping or empty pages.
- No unnecessary graphics, skill bars or image-based text.
- Avoid tables for layout.

Include relevant sections supported by the source resume:

- Contact Information
- Professional Summary
- Technical Skills
- Professional Experience
- Relevant Projects
- Education
- Certifications, when applicable

Do not force sections into the resume when the source contains no relevant information.

Use a consistent template across jobs. Optimize for readability and factual accuracy rather than excessive keyword repetition.

Support multi-page resumes and long bullet points without losing content.

## Phase 6 — Excel-based job selection and JD resolution

The existing generated Excel workbook is the job-selection interface.

Do not assume that a job ID can be resolved without reading the workbook or another existing source. Do not introduce a database.

### Step 1: Inspect the existing workbook data flow

Identify:

- The code that creates and writes the workbook.
- The actual workbook output path.
- Worksheet names and column names.
- The actual job ID field and its generation logic.
- Whether the full JD is stored in the workbook.
- Whether descriptions are persisted in another file or data structure.
- Whether the job URL is available.
- How duplicate jobs are handled.

Reuse the existing schema and logic. Do not redesign the workbook just for the resume generator.

### Step 2: Select a job from the workbook

Implement a job-selection workflow using the existing generated Excel workbook.

The workflow should:

1. Read the configured workbook.
2. Resolve the selected job using its actual identifier or an explicitly selected row.
3. Extract the job's available metadata.
4. Retrieve the full JD from the existing data source when available.
5. Pass the resolved job details to the common resume-generation pipeline.

Handle missing workbooks, missing columns, invalid IDs, duplicate IDs and empty records with useful error messages.

Never silently select the wrong job.

Do not hardcode column names until the real workbook schema has been inspected.

### Step 3: Resolve the full job description

Use the following priority:

1. Full JD stored in the selected workbook row.
2. Full JD available from an existing local artifact or data source referenced by the row.
3. Retrieval through the job URL if supported, accessible and permitted.
4. Manual JD input from the user.

A job URL does not guarantee that the full description can be retrieved. Account for expired listings, authentication requirements and access restrictions.

If the full description is unavailable, ask the user to paste it or provide a local text file.

Do not generate a supposedly tailored resume from only a job title and company name.

### Step 4: Support manual JD input

Allow the user to:

- Paste a JD interactively through the CLI, where practical.
- Supply a JD from a local text file.
- Provide company and role details optionally for output naming.
- Preview the proposed resume before final PDF generation.

Manual JD input must use the same tailoring, validation and PDF-rendering modules as workbook-based generation.

### Step 5: Preserve the existing crawler

- Do not modify the existing scraping provider.
- Do not break the current job-scoring workflow.
- Do not change the Excel schema unnecessarily.
- Do not introduce SQLite, PostgreSQL or another database.
- Do not alter the Windows Scheduled Task behavior.
- Keep resume generation an explicit user-triggered operation.
- Do not automatically generate resumes for every crawled job in this version.

If the workbook is regenerated or overwritten by the crawler, ensure that the resume generator reads the configured, current workbook and reports missing or stale records appropriately.

## Phase 7 — Output, filenames and generation metadata

Save generated PDFs under:

`data/resumes/`

Use filesystem-safe filenames based on company and job title.

For example:

`data/resumes/Company_Senior_Java_Engineer.pdf`

Requirements:

- Handle duplicate filenames without silently overwriting existing files.
- Record the source job ID when available.
- Record company, role, generation timestamp and output filename.
- Record the master resume source and model identifier.
- Record validation status.
- Use a small JSON metadata file or another lightweight local format if appropriate.
- Do not duplicate full resume content unnecessarily in metadata.
- Never store API credentials in metadata or logs.
- Add private resume files, generated PDFs and sensitive metadata to `.gitignore`.
- Do not create a database or an unnecessary persistence layer.

Keep output traceable to the selected job and the master resume version used.

## Phase 8 — Dependencies and configuration

Inspect `requirements.txt` before adding dependencies.

Use existing packages where appropriate.

Likely dependencies, if not already installed:

- OpenAI SDK for LLM integration.
- Pydantic for structured validation.
- ReportLab for PDF rendering.

Use the existing Excel library for workbook reading. Do not add another spreadsheet library unless necessary.

Use environment variables for secrets and configuration.

Provide a safe example configuration file without real credentials.

Avoid introducing unnecessary dependencies, frameworks or services.

## Phase 9 — Testing

Create automated tests using mocked LLM responses so the normal test suite does not incur API charges.

Test the following:

### Resume processing

- Existing master resume can be loaded.
- Empty or missing master resume produces a useful error.
- Existing scoring behavior remains compatible.
- Master resume is never modified by generation.

### JD analysis and validation

- Valid structured model responses.
- Malformed model responses.
- Empty job descriptions.
- Unsupported claims and missing evidence.
- Missing mandatory information.
- API errors and missing credentials.

### Excel integration

- Read the actual workbook schema.
- Select a job using its actual identifier.
- Handle duplicate or missing IDs.
- Handle missing workbook and required columns.
- Handle jobs without a full JD.
- Handle manual JD input independently of the workbook.
- Do not silently select the wrong record.

Use a representative test workbook fixture based on the real schema.

### PDF generation

- Generate a valid, non-empty PDF.
- Verify that its text is extractable.
- Handle long bullets and multi-page resumes.
- Handle missing optional sections.
- Verify that the output path and filename are correct.
- Prevent accidental overwrites.

### Backward compatibility

- Existing crawler commands continue to work.
- Existing Excel export remains functional.
- Existing resume scoring remains functional.
- Existing scheduled execution is unaffected.

Run the test suite and report actual results. Do not claim tests passed unless they were executed.

## Phase 10 — CLI integration and documentation

Follow the repository's existing CLI conventions.

Inspect `src/main.py` and implement the new commands using the actual project structure.

The intended workflows are:

### Workflow A: Generate for an existing job

Conceptually:

`python -m src.main resume --job-id JOB_ID`

This must resolve the job through the actual Excel workbook and existing data flow. The command must not assume the job description can be obtained from the ID alone.

### Workflow B: Generate from a local JD file

Conceptually:

`python -m src.main resume --jd-file path/to/job_description.txt`

### Workflow C: Paste a JD manually

Provide an interactive option consistent with the existing CLI.

Adapt the exact command syntax if the repository uses a different CLI pattern. Avoid introducing an incompatible CLI solely to match these examples.

Update README.md with:

- Setup and installation.
- Required environment variables.
- Master resume location.
- How to select a job from the generated workbook.
- How to supply a manual JD.
- How the JD is resolved when the workbook contains only a URL or metadata.
- How to preview and generate the PDF.
- Output location and naming.
- API cost considerations.
- Troubleshooting.
- Privacy and `.gitignore` behavior.

## Delivery requirements

Implement incrementally and keep the code maintainable.

Before changing code, present the repository inspection findings and implementation plan.

After implementation, report:

1. Files added and modified.
2. Actual modules reused.
3. How workbook-based job selection works.
4. How manual JD input works.
5. How the full JD is resolved.
6. How factual validation works and its limitations.
7. How the PDF is generated.
8. Exact commands to run.
9. Tests executed and their actual results.
10. Any known limitations or remaining manual steps.

Do not claim to have tested LinkedIn retrieval, API access or Windows Scheduled Task compatibility unless those behaviors were actually tested.

Build a focused local MVP using the existing codebase. Avoid unnecessary architecture changes.
