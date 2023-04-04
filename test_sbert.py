import numpy as np
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer
import os

def cos_sim(vec1, vec2):
    return np.dot(vec1, vec2)/(norm(vec1)*norm(vec2))

class lecture:
    def __init__(self, name, content, embeddings):
        self.name = name
        self.content = content
        self.embeddings = embeddings

# Algorithm S: Chunk the lecture content into smaller chunks and embed them
# using the SBERT model

def basic_parser(filename, model):
    """
    Takes in a .txt file and returns a list of strings, each string being a sentence.
    """
    path = os.path.join(os.getcwd(), "transcriptions", filename)
    with open(path, 'r') as f:
        content = f.read()
        sentences = content.split('\n')
    
    embeddings = model.encode(sentences)
    return lecture(filename, sentences, embeddings)

# Algorithm C: Pick the chunks that are the most similar to the question
# and put them into the context

def find_most_similar_sentences(question, lecture, n):
    """
    Takes in a question, a lecture, and a number n of sentences to return.
    Returns a list of the top n most similar sentences and the similarity score of each
    in a (score, sentence) format.
    """
    q_embedding = model.encode(question)
    cos_similarities = [cos_sim(q_embedding, sentence) for sentence in lecture.embeddings]
    top_entries = sorted(enumerate(cos_similarities), key=lambda x: x[1], reverse=True)[:n]
    # entry: (index, similarity score)

    return tuple(zip([entry[1] for entry in top_entries], [lecture.content[entry[0]] for entry in top_entries]))

if __name__ == "__main__":
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Parsing lecture content...")
    lecture_closures = basic_parser("Closures #2 2-15-23.txt", model)

    
    question = "What are anonymous functions in JavaScript?"
    print("Finding most similar sentences to '{}'...".format(question))
    top_sentences = find_most_similar_sentences(question, lecture_closures, 10)

    for entry in top_sentences:
        print(" -> {}: {}".format(entry[0], entry[1]))