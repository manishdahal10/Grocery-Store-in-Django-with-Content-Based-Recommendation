import csv
from collections import Counter
import re
import numpy as np

# Load the CSV file with correct column names
def load_data(file_path):
    products = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            products.append({
                'label': int(row['Class ID (int)']),
                'description': row['Product Description Path (str)'],
                'iconic_image_path': row['Iconic Image Path (str)']
            })
    return products

# Tokenize text
def tokenize(text):
    text = text.lower()
    words = re.findall(r'\w+', text)
    return words

# Build vocabulary
def build_vocabulary(products):
    vocab = set()
    for product in products:
        words = tokenize(product['description'])
        vocab.update(words)
    return sorted(vocab)

# Convert text to vector
def text_to_vector(text, vocabulary):
    text_words = tokenize(text)
    text_counter = Counter(text_words)
    vector = [text_counter.get(word, 0) for word in vocabulary]
    return vector

# Compute cosine similarity
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0

# Compute similarity matrix
def compute_similarity_matrix(products, vocabulary):
    num_products = len(products)
    similarity_matrix = np.zeros((num_products, num_products))
    
    vectors = [text_to_vector(p['description'], vocabulary) for p in products]
    
    for i in range(num_products):
        for j in range(num_products):
            if i != j:
                similarity_matrix[i][j] = cosine_similarity(vectors[i], vectors[j])
    
    return similarity_matrix

# Recommend products
def recommend_products(product_index, similarity_matrix, top_n=5):
    similar_indices = similarity_matrix[product_index].argsort()[-top_n:][::-1]
    return similar_indices

# Load and process data
file_path = 'dataset/classes.csv'
products = load_data(file_path)
vocabulary = build_vocabulary(products)
similarity_matrix = compute_similarity_matrix(products, vocabulary)

# # Example: Recommend products similar to the product with index 0
# recommended_indices = recommend_products(0, similarity_matrix)
# for index in recommended_indices:
#     print(f"Recommended product index: {index}, Description: {products[index]['description']}")
import pickle

# Saving the similarity matrix
np.save('similarity_matrix.npy', similarity_matrix)

# Optionally save the products list
with open('products.pkl', 'wb') as f:
    pickle.dump(products, f)
