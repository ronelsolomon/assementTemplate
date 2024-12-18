from flask import Flask, render_template

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
        question = request.json.get("question", "")
        if not question:
            return jsonify({"answer": "Please ask a question! 😅"}), 400

       
        LLM_API_URL = ""
        headers = {"Content-Type": "application/json"}
        payload = {"question": question}
        
        # Send a POST request to the LLM API
        response = requests.post(LLM_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error if the request fails
        
        # Parse the API response
        data = response.json()
        answer = data.get("answer", "Oops! The genius is confused. Try again!")
        
        return jsonify({"answer": answer})
    except requests.exceptions.RequestException as e:
        # Handle errors in the API request
        return jsonify({"answer": "Sorry, something went wrong while asking the Genius. Please try later!"}), 500

if __name__ == '__main__':
    app.run(debug=True)