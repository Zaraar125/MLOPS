from flask import Flask, request, jsonify, render_template
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load and train a Decision Tree model
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)

# Route to display the input form
@app.route('/')
def index():
    return render_template('index.html')

# Define the route for predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data (features from user input)
        feature_1 = float(request.form['feature_1'])
        feature_2 = float(request.form['feature_2'])
        feature_3 = float(request.form['feature_3'])
        feature_4 = float(request.form['feature_4'])

        # Prepare data for the model
        input_data = np.array([feature_1, feature_2, feature_3, feature_4]).reshape(1, -1)
        prediction = clf.predict(input_data)

        # Return the prediction to the frontend
        return render_template('index.html', prediction=int(prediction[0]))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
