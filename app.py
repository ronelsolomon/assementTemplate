from flask import Flask, render_template, request, jsonify
import PyPDF2
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load a pre-trained Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

PDF_FOLDER = "../pdfs"

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def generate_embeddings(text):
    """
    Generates embeddings for a given text using SentenceTransformer.
    """
    return model.encode(text)

def load_pdf_embeddings():
    """
    Loads and generates embeddings for all PDFs in the folder.
    Returns a dictionary with filenames and embeddings.
    """
    pdf_embeddings = {}
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, filename)
            text = extract_text_from_pdf(pdf_path)
            pdf_embeddings[filename] = generate_embeddings(text)
    return pdf_embeddings

def search_pdfs(query, pdf_embeddings):
    """
    Searches for a query in all PDF embeddings and ranks results by similarity.
    """
    query_embedding = generate_embeddings(query)
    results = []
    for filename, embedding in pdf_embeddings.items():
        similarity = cosine_similarity([query_embedding], [embedding])[0][0]
        results.append((filename, similarity))
    # Sort results by similarity in descending order
    results = sorted(results, key=lambda x: x[1], reverse=True)
    return results

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('self_assessment.html')


@app.route('/search')
def about():
    """
    Render the about.html template.

    Returns:
        HTML: The rendered about page.
    """
    return render_template('search_bar.html')

# Route to handle search queries
@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Extract the question from the POST request
        print("Hello")
        question = request.json.get("question", "").strip()
        if not question:
            return jsonify({"answer": "Please ask a question! 😅"}), 400

        # Load PDF embeddings
        pdf_embeddings = load_pdf_embeddings()
        
        # Search PDFs using the extracted question
        results = search_pdfs(question, pdf_embeddings)
        print(results)

        # Check if there are any results
        if results:
            top_result = results[0][0]  # Filename of the most relevant PDF
        else:
            top_result = "No relevant PDFs found for your query."

        # Combine response
        answer = f"Top PDF Match: {top_result}"
        return jsonify({"answer": answer})

    except Exception as e:
        print(f"Error: {e}")
        return ({"answer": "An error occurred while processing your request. Please try again later!"}), 500

if __name__ == '__main__':
    app.run(debug=True)