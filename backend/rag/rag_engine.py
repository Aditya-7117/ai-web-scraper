def build_documents(text, links):
    docs = []
    for link in links:
        docs.append({
            "content": text,
            "source": link["url"]
        })
    return docs

def answer_with_sources(llm, question, docs):
    context = "\n".join([f"{d['content']}\nSOURCE:{d['source']}" for d in docs[:3]])
    prompt = f"Answer the question using sources.\n{context}\nQ:{question}"
    return llm.generate_content(prompt).text
