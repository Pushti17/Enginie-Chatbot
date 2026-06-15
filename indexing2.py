import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load Model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load JSON Data
with open("college_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

titles = []
sources = []

# 🔥 Chunking Function (Improved)
def chunk_text(text, chunk_size=180, overlap=40):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 30:  # avoid tiny chunks
            chunks.append(chunk)

    return chunks


for page in data.get("pages", []):
    url = page.get("url", "")
    title = page.get("title", "").strip()
    main_text = page.get("main_text", "")
    tables = page.get("tables", [])

    # 🔥 Improved Table Conversion (Generic & Safe)
    table_text = ""
    for table in tables:
        for row in table:
            if len(row) >= 4:
                table_text += f"{row[0]} has details: {', '.join(row[1:])}. "
            else:
                table_text += " ".join(row) + ". "

    # Fallback title
    if not title:
        title = " ".join(main_text.split()[:10]) + "..."

    # Combine all content
    full_text = title + ". " + main_text + " " + table_text

    # 🔥 Apply chunking
    chunks = chunk_text(full_text)

    for chunk in chunks:
        titles.append(chunk)
        sources.append({
            "type": "webpage",
            "url": url,
            "title": title,
            "text": chunk
        })

# Convert to embeddings
embeddings = model.encode(titles, convert_to_numpy=True).astype("float32")

# FAISS Index
embedding_size = embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_size)
index.add(embeddings)

# Save index
faiss.write_index(index, "faiss_index_title.bin")

# Save sources
with open("sources_title.json", "w", encoding="utf-8") as f:
    json.dump(sources, f, indent=4, ensure_ascii=False)

print("✅ Chunk-based indexing completed successfully!")
print(f"Total chunks indexed: {len(titles)}")