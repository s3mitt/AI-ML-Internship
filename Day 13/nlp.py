import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

STOPWORDS = set(stopwords.words('english'))

documents = [
    "Natural Language Processing is a fascinating field of Artificial Intelligence.",
    "TF-IDF helps in finding the importance of a word in a document.",
    "Stopwords like 'is', 'the', 'a' do not add much meaning to text.",
    "Tokenization splits text into individual words or tokens.",
    "Machine learning models require clean and preprocessed text data.",
]

def preprocess(text):
    text = text.lower()
    tokens = word_tokenize(text)

    clean_tokens = [
        word for word in tokens
        if word.isalpha() and word not in STOPWORDS
    ]
    return clean_tokens

def main():
    print("=" * 70)
    print("STEP 1-3: Lowercasing + Tokenization + Stopword Removal")
    print("=" * 70)

    processed_docs = []
    for i, doc in enumerate(documents, 1):
        tokens = preprocess(doc)
        processed_docs.append(" ".join(tokens))
        print(f"\nDocument {i} (original): {doc}")
        print(f"Document {i} (tokens)  : {tokens}")

    print("\n" + "=" * 70)
    print("STEP 4: TF-IDF Vectorization")
    print("=" * 70)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_docs)

    feature_names = vectorizer.get_feature_names_out()
    tfidf_df = pd.DataFrame(
        tfidf_matrix.toarray(),
        columns=feature_names,
        index=[f"Doc{i+1}" for i in range(len(documents))]
    )

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    print("\nTF-IDF Matrix:\n")
    print(tfidf_df.round(3))

    tfidf_df.to_csv("tfidf_output.csv")
    print("\nSaved TF-IDF matrix to tfidf_output.csv")

if __name__ == "__main__":
    main()