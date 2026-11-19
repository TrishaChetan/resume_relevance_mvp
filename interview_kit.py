"""Interview kit: questions tailored to each candidate's resume vs. the JD.

- Claimed skills that matter most to the JD get *probe* questions that are hard
  to bluff ("walk me through...", "what went wrong...").
- Missing must-haves get *gap* questions (closest experience, ramp-up plan).
- An experience question is added when the JD's years requirement isn't met.

Questions come from a built-in bank for common skills, with sensible generic
fallbacks for anything else, so it works offline and costs nothing.
"""
from __future__ import annotations

import io
import re
import zipfile

BANK: dict[str, list[str]] = {
    "python": ["Walk me through a Python project you're proud of — how was the code organised and tested?",
               "When would you use a generator instead of a list, and why?",
               "How do you find out why a Python script is slow?"],
    "java": ["Explain how you've used interfaces vs. abstract classes in a real project.",
             "How does garbage collection affect a Java service you've worked on?"],
    "javascript": ["Explain the event loop with an example where it surprised you.",
                   "What's the difference between == and ===, and when has it bitten you?"],
    "typescript": ["How do you type an API response you don't fully control?",
                   "When is `any` acceptable, and what do you use instead?"],
    "c++": ["When would you choose a unique_ptr over a shared_ptr?", "Explain RAII with an example from your code."],
    "sql": ["Write a query for the top 3 customers by revenue per month — talk me through it.",
            "A query got slow after the table grew 10x. What do you check first?",
            "Explain the difference between an INNER and a LEFT JOIN with a case where it mattered."],
    "nosql": ["When did you pick a document database over a relational one, and what did you give up?"],
    "machine learning": ["Tell me about a model you trained: what was the baseline and how much did you beat it by?",
                         "How did you check the model wasn't overfitting?",
                         "How did you choose the evaluation metric for that problem?"],
    "deep learning": ["Describe a network you trained — what did you change when the loss stopped improving?",
                      "How do you decide between fine-tuning a pre-trained model and training from scratch?"],
    "nlp": ["How would you build a classifier for short, noisy text like tweets or support tickets?",
            "What's the difference between TF-IDF and embeddings, and when is TF-IDF still the better choice?"],
    "computer vision": ["How did you handle class imbalance or small datasets in a vision project?",
                        "Explain how you evaluated an object detector (IoU, mAP)."],
    "generative ai": ["How do you stop an LLM app from making things up?",
                      "Describe a prompt you iterated on — what changed between versions and why?",
                      "When would you use RAG instead of fine-tuning?"],
    "data analysis": ["Tell me about an analysis that changed a decision — what did you find and how did you show it?",
                      "How do you deal with missing or messy data before analysing it?"],
    "statistics": ["Explain a p-value to a non-technical manager.",
                   "How would you design an A/B test for a new checkout button?"],
    "data visualization": ["Show me (or describe) a chart you made — why that chart type?"],
    "power bi": ["How have you modelled data in Power BI — star schema, relationships, DAX measures?",
                 "Write a DAX measure for month-over-month growth."],
    "tableau": ["How do you keep a Tableau dashboard fast on a large dataset?"],
    "excel": ["Which Excel functions do you use most for analysis — XLOOKUP, pivot tables, Power Query?",
              "How would you reconcile two sheets of transactions that should match?"],
    "pandas": ["How do you merge two DataFrames and check nothing was duplicated or lost?",
               "groupby + agg vs. pivot_table — when do you use each?"],
    "scikit-learn": ["How do you build a Pipeline so preprocessing doesn't leak into validation?"],
    "tensorflow": ["How did you debug a TensorFlow model that wasn't learning?"],
    "pytorch": ["Walk me through a custom training loop you've written in PyTorch."],
    "spark": ["What causes a Spark job to shuffle, and how did you reduce it?",
              "Explain a time a Spark job ran out of memory and how you fixed it."],
    "etl": ["Describe a data pipeline you built: sources, schedule, and how you handled failures and reruns."],
    "airflow": ["How do you make an Airflow task safe to rerun (idempotent)?"],
    "kafka": ["How do consumer groups and partitions work together in Kafka?"],
    "html": ["How do you make a page accessible to screen-reader users?"],
    "css": ["Flexbox or grid — how do you decide for a given layout?"],
    "react": ["When does a React component re-render, and how have you stopped unnecessary re-renders?",
              "How do you manage state that many components need?"],
    "angular": ["Explain change detection in Angular and a performance issue you solved."],
    "node.js": ["How do you handle errors in async Express routes?",
                "What blocks the Node event loop, and how did you avoid it?"],
    "django": ["How do you avoid N+1 queries in the Django ORM?"],
    "flask": ["How do you structure a Flask app once it grows beyond one file?"],
    "fastapi": ["How do Pydantic models and dependencies work together in FastAPI?"],
    "spring": ["Explain dependency injection in Spring with an example from your code."],
    "rest api": ["How do you version a REST API without breaking existing clients?",
                 "Which HTTP status codes do you return for validation errors vs. auth errors?"],
    "microservices": ["When would you NOT split a system into microservices?"],
    "git": ["Merge vs. rebase — what does your team do and why?", "How do you undo a commit that's already pushed?"],
    "linux": ["A server's disk is full. Walk me through finding what's using it.",
              "How do you check which process is listening on a port?"],
    "oop": ["Explain one SOLID principle with an example from your own code."],
    "data structures": ["When would you use a hash map vs. a balanced tree?",
                        "Solve: find the first non-repeating character in a string — talk through complexity."],
    "testing": ["What do you unit-test vs. integration-test? Give an example of a bug a test caught."],
    "agile": ["How did your team handle a sprint where the scope changed halfway?"],
    "aws": ["Which AWS services have you used together, and how did you control access between them (IAM)?",
            "How would you cut the cost of an over-provisioned AWS setup?"],
    "azure": ["Describe an Azure deployment you've done end to end."],
    "gcp": ["Which GCP services have you used, and why those over alternatives?"],
    "docker": ["How do you make a Docker image smaller and faster to build?",
               "What's the difference between an image and a container?"],
    "kubernetes": ["A pod is in CrashLoopBackOff. How do you debug it?", "Deployment vs. StatefulSet — when do you use each?"],
    "ci/cd": ["Describe a CI/CD pipeline you set up: what runs on every push, and what blocks a release?"],
    "terraform": ["How do you manage Terraform state safely in a team?"],
    "cybersecurity": ["Walk me through how you'd investigate a suspicious login alert.",
                      "Explain the OWASP Top 10 risk you've dealt with most."],
    "networking": ["What happens when you type a URL into a browser, from DNS to the response?"],
    "communication": ["Tell me about explaining a technical problem to a non-technical stakeholder."],
    "leadership": ["Tell me about a time you helped a teammate who was stuck."],
    "problem solving": ["Describe the hardest bug you've fixed — how did you narrow it down?"],
    "teamwork": ["Tell me about a disagreement in a team project and how it was resolved."],
}
GENERIC_PROBE = ["Your resume mentions {s}. Walk me through the last time you used it — what was the task and what did you do?",
                 "What's something about {s} that tripped you up, and what did you learn?"]
GAP = ["The role needs {s}. What's the closest thing you've worked with, and how does it compare?",
       "If you joined next month, how would you get productive with {s} in your first few weeks?"]


def probe_questions(skill: str, n: int = 2) -> list[str]:
    qs = BANK.get(skill.lower()) or [q.format(s=skill) for q in GENERIC_PROBE]
    return qs[:n]


def build_kit(candidate: str, matched: list[str], missing: list[str], priorities: dict[str, str] | None = None,
              experience: str = "", max_probe_skills: int = 4) -> dict:
    """{candidate, probes: [(skill, [q...])], gaps: [(skill, [q...])], experience: [q...]}"""
    pri = priorities or {}
    rank = {"must": 0, "core": 1, "nice": 2}
    probes = sorted(matched, key=lambda s: (rank.get(pri.get(s, "core"), 1), s))[:max_probe_skills]
    must_missing = [s for s in missing if pri.get(s) == "must"]
    gaps = must_missing or [s for s in missing if pri.get(s) != "nice"][:2]
    exp_qs = []
    m = re.search(r"needs ([\d.]+)", experience or "")
    have = re.search(r"~([\d.]+) yrs", experience or "")
    if m and (not have or float(have.group(1)) < float(m.group(1))):
        exp_qs = [f"The role asks for {m.group(1)}+ years. Which project best shows you can work at that level?",
                  "What's the most complex piece of work you've owned from start to finish?"]
    return {"candidate": candidate,
            "probes": [(s, probe_questions(s)) for s in probes],
            "gaps": [(s, [q.format(s=s) for q in GAP]) for s in gaps[:3]],
            "experience": exp_qs}


def kit_markdown(kit: dict, job: str = "") -> str:
    out = [f"# Interview kit — {kit['candidate']}" + (f" ({job})" if job else ""), ""]
    if kit["probes"]:
        out += ["## Check the skills they claim", ""]
        for skill, qs in kit["probes"]:
            out.append(f"**{skill}**")
            out += [f"- [ ] {q}" for q in qs]
            out.append("")
    if kit["gaps"]:
        out += ["## Explore the gaps", ""]
        for skill, qs in kit["gaps"]:
            out.append(f"**{skill}** (missing from resume)")
            out += [f"- [ ] {q}" for q in qs]
            out.append("")
    if kit["experience"]:
        out += ["## Experience", ""] + [f"- [ ] {q}" for q in kit["experience"]] + [""]
    out += ["## Notes", "", "_Strong signals:_", "", "_Concerns:_", "", "_Recommendation:_ Hire / Next round / No", ""]
    return "\n".join(out)


def kits_zip(rows, priorities=None, job: str = "") -> bytes:
    """rows: iterable of dicts with Name/Resume, Matched, Missing, Experience (as in the results table)."""
    buf = io.BytesIO()
    used: set[str] = set()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            who = r.get("Name") or r.get("Resume") or "candidate"
            split = lambda v: [s.strip() for s in str(v or "").split(",") if s.strip()]
            kit = build_kit(who, split(r.get("Matched")), split(r.get("Missing")), priorities, str(r.get("Experience") or ""))
            safe = base = re.sub(r"[^A-Za-z0-9._-]+", "_", who).strip("_") or "candidate"
            n = 2
            while safe in used:  # two candidates with the same name
                safe, n = f"{base}-{n}", n + 1
            used.add(safe)
            z.writestr(f"interview-kit-{safe}.md", kit_markdown(kit, job))
    return buf.getvalue()
