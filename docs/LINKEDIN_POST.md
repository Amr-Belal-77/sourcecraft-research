# LinkedIn launch post

Replace the bracketed fields, add a screenshot or short screen recording, and keep the deployed
demo online before posting.

---

I turned a three-agent learning notebook into a deployable, source-aware research assistant. 🔎

Meet **SourceCraft Research**: enter a topic and three specialized AI agents collaborate to produce
a cited research brief:

1️⃣ A Researcher searches the web and converts results into evidence notes.

2️⃣ A Writer creates a structured brief for the selected audience and depth.

3️⃣ A Reviewer checks clarity, evidence, and citations—then either approves the result, sends weak
writing back for revision, or requests another research round when evidence is missing.

The most valuable lesson was that multi-agent systems are not just multiple prompts. The routing
logic matters: different failures should return to the agent responsible for fixing them.

I also moved the project beyond the notebook with:

✅ LangGraph state and conditional routing

✅ Gemini for synthesis and review

✅ Live web search with source links

✅ Streamlit UI and Markdown export

✅ Dependency injection and offline tests

✅ GitHub Actions CI and Docker deployment

✅ Iteration limits and graceful failure states

Demo: [DEPLOYED_APP_URL]

Code: https://github.com/Amr-Belal-77/sourcecraft-research

Next, I plan to specialize it as an **AI Research Paper Scout** and evaluate citation validity and
metric extraction against original papers.

I’d love feedback on the workflow and on other research domains where this architecture could be
useful.

#GenerativeAI #MultiAgentSystems #LangGraph #Gemini #Python #Streamlit #AIEngineering
