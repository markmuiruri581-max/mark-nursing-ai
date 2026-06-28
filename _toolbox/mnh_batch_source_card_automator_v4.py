"""
MNCH Batch Source Card Automator v4

Purpose:
- Reads selected further-reading URLs from urls.txt.
- Splits them into batches.
- Sends each batch to Gemini API using URL Context.
- Retries temporary failures AND empty responses.
- Saves successful source cards.
- Saves failed prompts for manual Google AI Studio fallback.
- Uses outputs_v4/ so it does not conflict with older runs.

Setup:
1. pip install -r requirements.txt
2. setx GEMINI_API_KEY "PASTE_YOUR_API_KEY_HERE"
3. Close and reopen PowerShell.
4. Paste selected URLs into urls.txt.
5. Run:
   python mnh_batch_source_card_automator_v4.py
"""

import os
import re
import sys
import time
import random
from pathlib import Path

from google import genai
from google.genai.types import GenerateContentConfig

MODULE_NAME = "Global Quality Maternal and Newborn Care - Module [EDIT_THIS]"

# Keep this small. URL Context can fail silently on heavier batches.
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "2"))

# Use URL-context-capable models. You can override with GEMINI_MODELS.
DEFAULT_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash",
]
MODELS = [m.strip() for m in os.getenv("GEMINI_MODELS", ",".join(DEFAULT_MODELS)).split(",") if m.strip()]

MAX_RETRIES_PER_MODEL = int(os.getenv("MAX_RETRIES_PER_MODEL", "3"))
RUN_STAGE2 = os.getenv("RUN_STAGE2", "false").lower() == "true"
FORCE_RERUN = os.getenv("FORCE_RERUN", "false").lower() == "true"

URLS_FILE = Path("urls.txt")
OUTPUT_DIR = Path("outputs_v4")
URL_RE = re.compile(r"https?://[^\s<>\")'\]]+")


def extract_urls(text: str) -> list[str]:
    raw = URL_RE.findall(text)
    cleaned = [u.rstrip(".,;:!?") for u in raw]
    seen = set()
    output = []
    for u in cleaned:
        if u not in seen:
            seen.add(u)
            output.append(u)
    return output


def stage1_prompt(module_name: str, urls: list[str], start_index: int) -> str:
    url_list = "\n".join(f"{start_index + i}. {u}" for i, u in enumerate(urls))
    return f"""# ROLE

Act as a senior consultant midwife, maternal-newborn quality improvement specialist, labour ward assessor, nursing lecturer, and evidence-based practice mentor.

# MY CONTEXT

I am a Bachelor of Science in Nursing student currently rotating through labour ward. I am taking the Coursera course **Global Quality Maternal and Newborn Care**.

My goal is to extract high-yield information that improves:
- Labour ward clinical reasoning
- Assessment and viva performance
- Maternal-newborn safety awareness
- Quality improvement thinking
- Documentation and communication skills
- Employability in maternal-newborn health, NGOs, public health programs, and government facilities

# STRICT SOURCE RULES

Analyze ONLY the URLs I provide below.
Do NOT use external guidelines, outside medical knowledge, outside statistics, or assumptions.
If a URL cannot be accessed, write: **URL not accessible. Paste the text or upload the PDF.**
If a point is not directly supported by the source, do not include it.
If information is missing, write: **Not discussed in the source.**
Do not browse beyond the provided URLs.
Do not add general knowledge just because it sounds clinically relevant.

# TOKEN-SAVING RULES

Keep output compact.
Use only high-yield bullets.
Avoid long paragraphs.
Do not summarize every paragraph.
Do not create separate long essays for each URL.
Do not quote more than one short phrase per source unless necessary.

# URL LIST

## Module: {module_name}

{url_list}

# TASK

For each URL, produce a compact source card using this exact format.

---

## Source Card [Number]: [Short Source Title]

**URL:** [Insert URL]

### 1. Main Point
- 3-5 bullets only.

### 2. Maternal-Newborn Importance
- 3-5 bullets only.

### 3. Labour Ward Relevance
Mention only if supported:
- Triage
- Labour monitoring
- Delivery care
- Postpartum care
- Immediate newborn care
- Referral or escalation

If not discussed, write: **Not discussed in the source.**

### 4. Quality / Safety Lessons
Extract source-supported points related to:
- Respectful care
- Communication
- Documentation
- Delay prevention
- Referral systems
- Staffing
- Supplies
- Clinical governance
- Audit or quality improvement

### 5. High-Yield Assessment Points
List 3-7 points I should remember for labour ward assessment or viva.

### 6. Practical Actions
List only practical actions directly supported by the source.

### 7. Employment Advantage
List 2-5 competencies this source helps me demonstrate in interviews, CV, clinical placement, NGO work, or maternal-newborn health programs.

### 8. Limitations / Gaps
State what the source does not cover or what uncertainty it mentions.

---

# FINAL OUTPUT AFTER ALL SOURCE CARDS

## Batch Synthesis Table

| Theme | Source Numbers | Key Takeaway | Labour Ward Use | Quality Improvement Use |
|---|---:|---|---|---|

## Top 10 Takeaways From This Batch

Rank the 10 highest-value lessons from all URLs combined.

## Assessment Bank

Create only 10 questions total from the batch.

| Question | Model Answer | Source Number |
|---|---|---|

## One-Minute Revision Sheet

Create a concise revision sheet I can read before labour ward assessment.

# FINAL CHECK

Before answering, remove unsupported information. Every claim must be traceable to one of the provided URLs.
"""


def stage2_prompt(module_name: str, source_cards: str) -> str:
    return f"""# ROLE

Act as a senior consultant midwife, maternal-newborn quality improvement specialist, labour ward assessor, nursing lecturer, and examiner.

# MY CONTEXT

I am a Bachelor of Science in Nursing student rotating through labour ward. I am using further-reading materials from the Coursera course **Global Quality Maternal and Newborn Care**.

I have already processed the module readings into source cards. Your task is to synthesize them into one compact, high-yield module revision document.

# STRICT RULES

Use ONLY the source cards pasted below.
Do NOT add external facts, external guidelines, statistics, or assumptions.
Do NOT expand beyond the evidence contained in the source cards.
If something is not present in the source cards, write: **Not covered in the source cards.**
Avoid repetition.
Prioritize clinical usefulness, quality improvement thinking, labour ward assessment performance, and employability.

# MODULE

{module_name}

# SOURCE CARDS

{source_cards}

# TASK

Create a final module synthesis using the structure below.

# Module Master Summary

## 1. Module-Level Executive Summary
Summarize the entire module’s further-reading material in 12-18 high-yield bullets.

## 2. Core Themes Across the Readings

| Core Theme | What It Means | Sources Supporting It | Why It Matters |
|---|---|---:|---|

## 3. Labour Ward Application

| Labour Ward Area | Key Lessons From Readings | Practical Use | Source Cards |
|---|---|---|---:|
| Triage |  |  |  |
| First Stage of Labour |  |  |  |
| Second Stage of Labour |  |  |  |
| Third Stage of Labour |  |  |  |
| Immediate Postpartum Care |  |  |  |
| Immediate Newborn Care |  |  |  |
| Referral / Escalation |  |  |  |

Only fill sections supported by the source cards. Otherwise write: **Not covered.**

## 4. Quality Maternal-Newborn Care Framework

Use compact bullets under:
- Clinical effectiveness
- Patient safety
- Respectful maternity care
- Communication
- Documentation
- Referral systems
- Staffing and resources
- Quality improvement
- Leadership and supervision

## 5. What Makes Me Clinically Stronger From This Module

| Competency | What I Should Know | How I Should Demonstrate It in Labour Ward |
|---|---|---|

## 6. High-Yield Assessment and Viva Preparation

Create 20 likely questions.

| Question | Model Answer | Source Card Basis |
|---|---|---|

## 7. Interview and Employability Preparation

Create 10 interview-style questions.

| Interview Question | Strong Model Answer | Competency Demonstrated |
|---|---|---|

## 8. Practical Labour Ward Checklist

Group by:
- Before care
- During labour
- During delivery
- After delivery
- Newborn care
- Documentation
- Escalation
- Communication

Only include source-supported actions.

## 9. Red Flags and Safety Risks

| Risk / Problem | Why It Matters | Prevention or Response | Source Card |
|---|---|---|---:|

## 10. Quality Improvement Opportunities

| Problem Area | Possible QI Response | Measurement Idea | Source Card |
|---|---|---|---:|

## 11. One-Page Revision Sheet
Create a dense one-page revision sheet.

## 12. Flashcards
Create 25 flashcards.

| Front | Back |
|---|---|

## 13. What This Module Trains Me to Notice That Average Students Miss
Focus on clinical reasoning, system failures, communication risks, documentation gaps, patient safety threats, respectful care, escalation judgment, and quality improvement opportunities.

# FINAL CHECK

Remove unsupported information. Keep synthesis compact. Do not add external medical knowledge.
"""


def retryable(exc: Exception) -> bool:
    text = str(exc).lower()
    return (
        "empty model response" in text
        or "empty response" in text
        or "503" in text
        or "unavailable" in text
        or "high demand" in text
        or "temporarily" in text
        or "429" in text
        or "rate limit" in text
        or "quota" in text
        or "timeout" in text
        or "deadline" in text
    )


def generate_with_retries(client, prompt: str, use_url_context: bool) -> tuple[str, str]:
    config = GenerateContentConfig(tools=[{"url_context": {}}]) if use_url_context else None
    last_error = None

    for model in MODELS:
        for attempt in range(1, MAX_RETRIES_PER_MODEL + 1):
            try:
                print(f"  Model: {model} | attempt {attempt}/{MAX_RETRIES_PER_MODEL}")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                text = response.text or ""
                if not text.strip():
                    raise RuntimeError("Empty model response.")
                return text, model

            except Exception as exc:
                last_error = exc
                print(f"  Failed: {type(exc).__name__}: {exc}")

                if not retryable(exc):
                    raise

                wait = min(90, (attempt * 12) + random.randint(3, 12))
                print(f"  Waiting {wait} seconds before retry...")
                time.sleep(wait)

        print(f"  Switching model after repeated failure: {model}")

    raise RuntimeError(f"All models failed. Last error: {last_error}") from last_error


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set.")
        print('Run: setx GEMINI_API_KEY "PASTE_YOUR_API_KEY_HERE"')
        print("Then close and reopen PowerShell.")
        sys.exit(1)

    if not URLS_FILE.exists():
        URLS_FILE.write_text("# Paste one selected further-reading URL per line.\n", encoding="utf-8")
        print("Created urls.txt. Paste your URLs into it, then run again.")
        sys.exit(0)

    urls = extract_urls(URLS_FILE.read_text(encoding="utf-8"))
    if not urls:
        print("No valid URLs found in urls.txt.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    client = genai.Client(api_key=api_key)

    print(f"Module: {MODULE_NAME}")
    print(f"URLs found: {len(urls)}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Models: {', '.join(MODELS)}")
    print(f"Output folder: {OUTPUT_DIR}")

    all_cards = []
    failed = []

    for batch_no, start in enumerate(range(0, len(urls), BATCH_SIZE), start=1):
        end = start + len(urls[start:start + BATCH_SIZE])
        batch = urls[start:start + BATCH_SIZE]
        source_range = f"sources_{start + 1:03d}_{end:03d}"
        prompt = stage1_prompt(MODULE_NAME, batch, start + 1)

        prompt_file = OUTPUT_DIR / f"{source_range}_prompt.md"
        prompt_file.write_text(prompt, encoding="utf-8")

        output_file = OUTPUT_DIR / f"{source_range}_source_cards.md"

        if output_file.exists() and output_file.stat().st_size > 0 and not FORCE_RERUN:
            print(f"\nSkipping {source_range}; output exists.")
            all_cards.append(f"\n\n# {source_range}\n\n{output_file.read_text(encoding='utf-8')}")
            continue

        print(f"\nProcessing {source_range}")

        try:
            output, used_model = generate_with_retries(client, prompt, use_url_context=True)
            final = f"<!-- Generated with model: {used_model} -->\n\n{output}"
            output_file.write_text(final, encoding="utf-8")
            all_cards.append(f"\n\n# {source_range}\n\n{final}")
            print(f"Saved: {output_file}")

        except Exception as exc:
            failed.append(source_range)
            failed_file = OUTPUT_DIR / f"{source_range}_FAILED.md"
            failed_file.write_text(
                "# Failed batch\n\n"
                f"Source range: {source_range}\n\n"
                "## URLs\n\n"
                + "\n".join(f"- {u}" for u in batch)
                + "\n\n## Error\n\n"
                + str(exc)
                + "\n\n## Manual fallback\n\n"
                + f"Copy the prompt from `{prompt_file.name}` and paste it into Google AI Studio manually.\n",
                encoding="utf-8",
            )
            print(f"Saved failure report: {failed_file}")

    combined = "\n".join(all_cards).strip()
    combined_file = OUTPUT_DIR / "all_source_cards_combined.md"
    combined_file.write_text(combined, encoding="utf-8")
    print(f"\nSaved combined source cards: {combined_file}")

    placeholder_prompt = stage2_prompt(MODULE_NAME, "[PASTE contents of all_source_cards_combined.md here]")
    stage2_file = OUTPUT_DIR / "stage2_final_synthesis_prompt.md"
    stage2_file.write_text(placeholder_prompt, encoding="utf-8")
    print(f"Saved Stage 2 prompt: {stage2_file}")

    if failed:
        print("\nFailed batches:")
        print(", ".join(failed))
        print("Manual fallback: open the matching *_prompt.md files and paste them into Google AI Studio.")
        print("Or wait 10-30 minutes and rerun this script.")
        sys.exit(2)

    if RUN_STAGE2:
        print("\nRUN_STAGE2=true. Running Stage 2 automatically.")
        final_output, used_model = generate_with_retries(
            client,
            stage2_prompt(MODULE_NAME, combined),
            use_url_context=False,
        )
        final_file = OUTPUT_DIR / "module_master_synthesis.md"
        final_file.write_text(f"<!-- Generated with model: {used_model} -->\n\n{final_output}", encoding="utf-8")
        print(f"Saved final synthesis: {final_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()
