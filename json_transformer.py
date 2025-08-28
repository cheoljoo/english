import json
import re

def summarize_text(text):
    # Summarization by taking sentences up to a maximum length.
    sentences = text.split('.')
    summary = ""
    max_summary_length = 2000
    for sentence in sentences:
        if len(summary) + len(sentence) + 1 < max_summary_length:
            summary += sentence + "."
        else:
            break
    if not summary: # if the first sentence is too long or no sentences
        return text[:max_summary_length].strip()
    return summary.strip()

def generate_questions(text):
    questions = []
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]

    # Question 1: Main subject
    if sentences:
        questions.append("What is the main subject of this article?")

    # Question 2: Key entities (people, organizations, places)
    # Look for capitalized words that are likely proper nouns
    entities = set()
    for sentence in sentences:
        words = re.findall(r'\b[A-Z][a-z]+\b', sentence) # Simple regex for capitalized words
        for word in words:
            # Filter out common words that might start a sentence but aren't entities
            if word.lower() not in ["the", "a", "an", "in", "on", "at", "for", "with", "by", "of", "to", "and", "but", "or", "is", "are", "was", "were", "it", "he", "she", "they", "we", "you"]:
                entities.add(word)
    
    if len(entities) > 0 and len(questions) < 3:
        # Take up to 2 distinct entities to form a question
        entity_list = list(entities)[:2]
        if len(entity_list) == 1:
            questions.append(f"Who or what is {entity_list[0]} and what is their role?")
        elif len(entity_list) > 1:
            questions.append(f"What is the significance of {entity_list[0]} and {entity_list[1]} in the article?")

    # Question 3: Key action or event
    if len(questions) < 3 and sentences:
        action_found = False
        for i in range(min(len(sentences), 3)): # Check first 3 sentences
            sentence = sentences[i]
            if re.search(r'\b(announced|said|reported|developed|launched|created|began|started|found|discovered|explained|revealed)\b', sentence, re.IGNORECASE):
                questions.append(f"What key event or action is described in the article?")
                action_found = True
                break
        if not action_found:
            questions.append("What is the primary outcome or message conveyed?")

    return questions[:3]


def infer_topic(source_text):
    lines = [line.strip() for line in source_text.split('\n') if line.strip()]
    for line in lines:
        # Heuristic to find a title-like line: not too long, starts with a capital letter
        if 10 < len(line) < 100 and line[0].isupper() and not line.endswith('.'):
            return line
    # Fallback: take the first reasonable sentence
    sentences = [s.strip() for s in source_text.split('.') if s.strip()]
    if sentences:
        return sentences[0]
    return "No specific topic found"


with open('/usr/src/app/contents-today.temp.json', 'r') as f:
    data = json.load(f)

output_data = []
for item in data:
    source_text = item.get('source', '')
    topic = item.get('topic')
    if not topic:
        topic = infer_topic(source_text)

    if not source_text or len(source_text) < 50: # Skip if source is too short or missing
        continue

    new_item = {
        "date": "2025-08-28",
        "URL": item.get('URL'),
        "topic": topic,
        "source": source_text,
        "summary": summarize_text(source_text),
        "questions": generate_questions(source_text)
    }
    output_data.append(new_item)

with open('/usr/src/app/contents-today.json', 'w') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)