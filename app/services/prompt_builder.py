from typing import List

from app.models.retrieval_result import RetrievalResult


def build_incident_analysis_prompt(
    question: str,
    retrieved_chunks: List[RetrievalResult],
) -> str:
    context_parts = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"Chunk {index}:\n"
            f"Chunk ID: {chunk.chunk_id}\n"
            f"Metadata: {chunk.metadata}\n"
            f"Document:\n{chunk.document}\n"
        )

    context = "\n---\n".join(context_parts)

    prompt = f"""
You are an AI production incident assistant.

Your job is to analyze production log context and answer the user's question.

Instructions:
- Use only the provided retrieved log chunks.
- Do not invent causes that are not supported by the logs.
- Clearly identify the most likely root cause if possible.
- Mention supporting evidence from the retrieved chunks.
- If the evidence is insufficient, say that clearly.
- Keep the answer clear and concise.

User Question:
{question}

Retrieved Context:
{context}

Return your answer in this format:

Root Cause:
<your answer>

Evidence:
- <evidence point 1>
- <evidence point 2>

Recommended Next Step:
- <next step>
"""
    return prompt.strip()