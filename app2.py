from flask import Flask, request, jsonify, render_template
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
from flask_cors import CORS
import re

# --- Initialize Flask ---
app = Flask(__name__)
CORS(app)

# --- Load Models ---
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
llm = OllamaLLM(model="mistral:7b-instruct")

# --- Load FAISS + Data ---
index = faiss.read_index("faiss_index_title.bin")

with open("sources_title.json", "r", encoding="utf-8") as f:
    sources = json.load(f)

with open("general_responses.json", "r", encoding="utf-8") as f:
    general_responses = json.load(f)

# --- CONFIG ---
TOP_K = 5
MAX_CHUNKS = 3
MAX_DISTANCE = 1.0   # for L2 (tune 0.8–1.2)


# 🔹 Normalize Query
def normalize_query(query):
    return query.lower().strip()


# 🔹 Safe Custom Expansion (optional but controlled)
CUSTOM_SYNONYMS = {
    "it": ["information technology"],
    "dept": ["department"],
    "prof": ["professor", "faculty"]
}

def clean_query(query):
    query = query.lower().strip()
    query = re.sub(r'[^\w\s]', '', query)  # remove punctuation
    return query

def expand_query_safe(query):
    words = query.split()
    expanded = words.copy()

    for word in words:
        if word in CUSTOM_SYNONYMS:
            expanded.extend(CUSTOM_SYNONYMS[word])

    return " ".join(expanded)


# 🔹 LLM Call (STRICT)
def run_llm(query, context):
    prompt = f"""
You are an AI assistant for SSEC(Shantilal Shah Engineering College) college.

- You have to give answers from given user query and context
- According to question you can choose whether to give answer in detail or specific
- you can give general questions answers like "who are you" or "tell me about college" by yourself in short
- please answer queries like "Hello", "How are you", "who are you" etc by yourself with good reply
- If answer is not clearly present or it is totally out of context, say: "No relevant information found, For more information you can visit the wensite "https://ssgec.ac.in/"." and do not give hallucination answer without the context
- Keep answer accurate
- some general questions "how many departments are there":"6 departments are there"
- If quetion is about something and the context have 2 different thing, but you are getting answer from specif thing then only show that information, no extra information out of question.

User Query:
{query}

Context:
{context}

Answer:
"""
    try:
        response = llm.invoke(prompt).strip()
        return response
    except Exception:
        return ""


# 🔥 Core Search Logic
def search_and_answer(query):

    query = normalize_query(query)

    # ✅ Step 1: Handle General Responses (like "who are you")
    query_clean = clean_query(query)

    for key, answer in general_responses.items():
        key_clean = clean_query(key)

        # ✅ Exact match OR very close match
        if query_clean == key_clean:
            return {
                "title": key,
                "answer": answer,
                "reference_url": "N/A"
            }

    # ✅ Step 2: Expand safely (optional)
    query_expanded = expand_query_safe(query)

    # ✅ Step 3: Embedding
    query_embedding = embedding_model.encode(
        query_expanded, convert_to_numpy=True
    ).astype("float32")

    # ✅ Step 4: FAISS Search
    distances, indices = index.search(np.array([query_embedding]), TOP_K)

    # DEBUG (optional)
    # print("Distances:", distances[0])

    # ✅ Step 5: Strict Filtering (L2 distance)
    selected_matches = []

    for i, idx in enumerate(indices[0]):
        if idx >= len(sources):
            continue

        score = distances[0][i]

        if score <= MAX_DISTANCE:
            selected_matches.append(sources[idx])

    # fallback (ONLY best one)
    if not selected_matches:
        best_idx = indices[0][0]
        if best_idx < len(sources):
            selected_matches.append(sources[best_idx])

    # limit chunks
    selected_matches = selected_matches[:MAX_CHUNKS]

    # ❌ If still weak match → reject early
    if distances[0][0] > 1.5:
        return {
            "title": "No Relevant Information Found",
            "answer": "No relevant information found.",
            "reference_url": "N/A"
        }

    # ✅ Step 6: Build Context
    context_text = "\n\n".join([m["text"] for m in selected_matches])

    # ✅ Step 7: LLM Answer
    answer = run_llm(query, context_text)

    if not answer or "No relevant information found" in answer:
        return {
            "title": "No Relevant Information Found",
            "answer": "No relevant information found.",
            "reference_url": "N/A"
        }

    # ✅ Step 8: Title (BEST MATCH ONLY)
    title = selected_matches[0]["title"]

    # ✅ Step 9: Clean References (max 2)
    urls = list(dict.fromkeys([m["url"] for m in selected_matches]))
    reference_urls = "\n".join(urls[:2])

    return {
        "title": title,
        "answer": answer,
        "reference_url": reference_urls
    }


# --- Routes ---
@app.route("/")
def home():
    return render_template("enginie.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")

    if not query.strip():
        return jsonify({
            "title": "Error",
            "answer": "Please enter a valid query.",
            "reference_url": ""
        })

    result = search_and_answer(query)
    return jsonify(result)


# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)