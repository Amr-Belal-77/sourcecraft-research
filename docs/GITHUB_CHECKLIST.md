# GitHub publishing checklist

## Before the first push

- Replace the repository URL placeholders in `docs/LINKEDIN_POST.md`.
- Add your name, portfolio link, and contact details to the GitHub repository profile if desired.
- Run `python -m ruff check .` and `python -m pytest`.
- Confirm `.env` and `.streamlit/secrets.toml` are not tracked.
- Add one clean UI screenshot or a 20–40 second GIF to the README after the first real run.

## Create and publish the repository

Run these commands only after creating an empty `sourcecraft-research` repository in your GitHub
account:

```bash
git init
git add .
git commit -m "Build deployable three-agent research assistant"
git branch -M main
git remote add origin https://github.com/Amr-Belal-77/sourcecraft-research.git
git push -u origin main
```

Recommended GitHub description:

> Source-aware three-agent research assistant with LangGraph, Gemini, Streamlit, tests, CI, and
> Docker.

Recommended repository topics:

`multi-agent-systems`, `langgraph`, `gemini`, `generative-ai`, `streamlit`, `python`,
`research-assistant`, `llm-agents`

## After the push

- Confirm GitHub Actions passes on Python 3.11 and 3.13.
- Deploy `streamlit_app.py` on Streamlit Community Cloud and add `GOOGLE_API_KEY` in app secrets.
- Put the live URL in the repository About section and in `docs/LINKEDIN_POST.md`.
- Pin the repository on your GitHub profile.
- Add the project to your CV with a measurable result after evaluating real research runs.

Suggested CV bullet:

> Built and deployed a source-aware three-agent research assistant using LangGraph and Gemini;
> implemented evidence-based routing, iterative quality review, Streamlit delivery, offline graph
> tests, GitHub Actions CI, and Docker packaging.
