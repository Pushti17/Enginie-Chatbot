import json
import re
import time
from langchain_ollama import OllamaLLM

# --- Load your data ---
with open("sources_title.json", "r", encoding="utf-8") as f:
    sources = json.load(f)

# --- Initialize LLM ---
llm = OllamaLLM(model="mistral:7b-instruct")

dataset = []

# --- Config ---
MAX_CHARS = 1200
SLEEP_TIME = 1


# 🔹 Clean LLM output
def clean_llm_output(response):
    response = response.strip()
    response = re.sub(r"```json|```", "", response)
    return response


# 🔹 Prompt generator
def create_prompt(context, title):
    return f"""
Generate 3 high-quality question-answer pairs from the given college information.

STRICT RULES:
- Questions must be realistic student/user queries
- Answers must ONLY use the given context
- Do NOT hallucinate or add extra info
- Keep answers concise (2–4 lines)
- Avoid repeating same type of questions

Return ONLY valid JSON:
[
  {{"question": "...", "answer": "..."}},
  {{"question": "...", "answer": "..."}},
  {{"question": "...", "answer": "..."}}
]

Title: {title}

Context:
{context}
"""


# 🔥 Loop through data
for i, item in enumerate(sources):

    title = item.get("title", "").strip()
    context = item.get("text", "").strip()

    # Skip bad/empty chunks
    if len(context) < 50:
        continue

    # Limit context size
    context = context[:MAX_CHARS]

    print(f"Processing {i+1}/{len(sources)}: {title}")

    try:
        prompt = create_prompt(context, title)
        response = llm.invoke(prompt)

        response = clean_llm_output(response)

        # Parse JSON
        qa_pairs = json.loads(response)

        for qa in qa_pairs:
            question = qa.get("question", "").strip()
            answer = qa.get("answer", "").strip()

            if not question or not answer:
                continue

            # ✅ Final training format (QLoRA-ready)
            dataset.append({
                "instruction": "Answer based on context",
                "input": f"Context: {context}\n\nQuestion: {question}",
                "output": answer
            })

    except Exception as e:
        print(f"❌ Error at chunk {i}: {e}")
        continue

    time.sleep(SLEEP_TIME)


# --- Save dataset ---
with open("finetune_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4, ensure_ascii=False)

print(f"\n✅ Dataset generated successfully!")
print(f"Total samples: {len(dataset)}")