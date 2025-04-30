




from openai import OpenAI
from datetime import datetime, timedelta
import re


def generate_answer(query: str, chunks: list):
    if not chunks:
        return "I couldn't find any relevant information for that property."

    context = "\n\n".join(doc.page_content for doc in chunks)

    prompt = f"""You are a real estate assistant helping manage property documents.

Query: {query}

Context:
{context}

Answer:"""

    response = OpenAI().chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for property management."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()






def generate_reasoned_answer(query: str, chunks: list):
    if not chunks:
        return "I couldn't find any relevant information for that property."

    context = "\n\n".join(doc.page_content for doc in chunks)

    prompt = f"""
You are a smart and logical assistant for real estate document management.
You have access to property-related documents that might contain structured or semi-structured information like payment schedules, dates, and rules.

Use reasoning to infer answers based on the context, even if some details must be calculated or interpreted (e.g., next payment = last payment + 1 month).

Query: {query}

Context:
{context}

If the document states a rule such as recurring monthly payments and provides the last payment date, compute the next payment date accordingly.

Answer:
"""

    response = OpenAI().chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for property management who reasons about financial documents."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

