import json
import re
from datetime import datetime

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

    # Question 1: Main subject/idea
    if sentences:
        questions.append("What is the primary focus or main idea of this article?")

    # Question 2: Key entities (people, organizations, places)
    # Look for capitalized words that are likely proper nouns, appearing more than once
    entity_candidates = {}
    for sentence in sentences:
        # Find sequences of capitalized words
        matches = re.findall(r'\b[A-Z][a-z]*(?:\s[A-Z][a-z]*)*\b', sentence)
        for match in matches:
            # Filter out common words that might start a sentence but aren't entities
            if match.lower() not in ["the", "a", "an", "in", "on", "at", "for", "with", "by", "of", "to", "and", "but", "or", "is", "are", "was", "were", "it", "he", "she", "they", "we", "you", "this", "that", "these", "those"]:
                entity_candidates[match] = entity_candidates.get(match, 0) + 1

    # Select entities that appear more than once or are significant
    key_entities = [entity for entity, count in entity_candidates.items() if count > 1 or (len(entity.split()) > 1 and count > 0)]
    key_entities = sorted(key_entities, key=lambda x: entity_candidates[x], reverse=True)[:2] # Take top 2 by frequency

    if len(key_entities) > 0 and len(questions) < 3:
        if len(key_entities) == 1:
            questions.append(f"Who or what is {key_entities[0]} and what is their role or significance in the article?")
        elif len(key_entities) > 1:
            questions.append(f"What is the relationship or interaction between {key_entities[0]} and {key_entities[1]} as described in the article?")

    # Question 3: Key action, event, or outcome
    if len(questions) < 3 and sentences:
        action_keywords = r'\b(announced|said|reported|developed|launched|created|began|started|found|discovered|explained|revealed|impact|consequence|result|outcome)\b'
        action_found = False
        for i in range(min(len(sentences), 5)): # Check first 5 sentences for action keywords
            sentence = sentences[i]
            if re.search(action_keywords, sentence, re.IGNORECASE):
                questions.append(f"What significant event, action, or outcome is discussed in the article?")
                action_found = True
                break
        if not action_found:
            questions.append("What are the main implications or consequences discussed in the article?")

    return questions[:3]



