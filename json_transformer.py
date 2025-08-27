
import json

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
    sentences = [s.strip() for s in text.split('.') if s.strip()]

    # Try to generate questions based on common patterns
    if sentences:
        # Question 1: What is the article about? (General topic)
        questions.append("What is the main subject of this article?")

        # Question 2: Who or what is involved? (Entities)
        # Look for capitalized words that might be names or key terms
        entities = set()
        for sentence in sentences:
            words = sentence.split()
            for word in words:
                if word and word[0].isupper() and len(word) > 1 and word.lower() not in ["the", "a", "an", "in", "on", "at", "for", "with", "by", "of", "to", "and", "but", "or", "is", "are", "was", "were"]:
                    entities.add(word.strip(".,;:'\""))
        if entities:
            questions.append(f"Who or what are the key entities mentioned?")
        
        # Question 3: What happened or what is the main point? (Action/Outcome)
        # Look for verbs or action-oriented phrases
        if len(questions) < 3:
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

    new_item = {
        "date": "2025-08-27",
        "URL": item.get('URL'),
        "topic": topic,
        "source": source_text,
        "summary": summarize_text(source_text),
        "questions": generate_questions(source_text)
    }
    output_data.append(new_item)

with open('/usr/src/app/contents-today.json', 'w') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

