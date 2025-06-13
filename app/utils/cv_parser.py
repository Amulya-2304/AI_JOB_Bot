import spacy

nlp = spacy.load("en_core_web_sm")

def extract_cv_data(text):
    """
    Extracts useful information from resume text.
    Returns named entities and noun chunks that may relate to skills and experience.
    """
    doc = nlp(text)

    entities = [(ent.label_, ent.text) for ent in doc.ents]
    skills = [chunk.text for chunk in doc.noun_chunks if len(chunk.text) > 2]

    return {
        "entities": entities,
        "skills": list(set(skills))  # Remove duplicates
    }