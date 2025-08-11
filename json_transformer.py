
import json

def summarize_text(text):
    # Simple summarization by taking the first few sentences.
    sentences = text.split('.')
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) + 1 < 400:
            summary += sentence + "."
        else:
            break
    if not summary: # if the first sentence is too long
        return text[:400]
    return summary.strip()

def generate_questions(text):
    # This is a simple heuristic and might not produce perfect questions.
    questions = []
    sentences = text.split('.')
    
    # Question 1: About the main subject
    if "is" in sentences[0] or "are" in sentences[0]:
        parts = sentences[0].split(" is ") if " is " in sentences[0] else sentences[0].split(" are ")
        if len(parts) > 1:
            questions.append(f"What is {parts[0].strip()}?")

    # Question 2: "Why" question if "because" is present
    for sentence in sentences:
        if "because" in sentence.lower():
            parts = sentence.lower().split("because")
            questions.append(f"Why {parts[0].strip()}?")
            break
            
    # Question 3: General question
    if len(questions) < 3:
        questions.append("What is the main takeaway from this article?")

    # Ensure we have at most 3 questions
    return questions[:3]


with open('/usr/src/app/contents-today.temp.json', 'r') as f:
    data = json.load(f)

output_data = []
for item in data:
    source_text = item.get('source', '')
    new_item = {
        "date": "2025-08-11",
        "URL": item.get('URL'),
        "topic": item.get('topic'),
        "source": source_text,
        "summary": summarize_text(source_text),
        "questions": generate_questions(source_text)
    }
    output_data.append(new_item)

with open('/usr/src/app/contents-today.json', 'w') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)
