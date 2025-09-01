import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from prometheus_client import Gauge
import os
import random
import json   # <-- add this

# Define prometheus metric for accuracy
accuracy_metric = Gauge('model_accuracy', 'Accuracy of the ML model')

def train_and_save_model():
    # Load dataset
    iris = load_iris()

    # Use a random seed for train/test split to get different results each run
    random_seed = random.randint(0, 1000)
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=random_seed)

    # Train model
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    # Test model
    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    accuracy_metric.set(accuracy)

    # Compute classification report (dict + text version)
    report_dict = classification_report(
        y_test, preds, target_names=iris.target_names, output_dict=True
    )
    report_text = classification_report(
        y_test, preds, target_names=iris.target_names
    )

    # Define output directories
    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    os.makedirs(model_dir, exist_ok=True)

    # Save model
    joblib.dump(model, os.path.join(model_dir, 'logistic_regression.joblib'))

    # Save metrics as text
    with open(os.path.join(model_dir, 'metrics.txt'), 'w') as f:
        f.write(f'Accuracy: {accuracy:.4f}\n')
        f.write(f'Random seed used for split: {random_seed}\n\n')
        f.write("Classification Report:\n")
        f.write(report_text)

    # ✅ Save metrics as JSON for Streamlit
    metrics = {
        "accuracy": accuracy,
        "classification_report": report_dict,
        "random_seed": random_seed
    }

    with open(os.path.join(os.path.dirname(__file__), 'metrics.json'), 'w') as f:
        json.dump(metrics, f)

    print(f'Model trained with accuracy: {accuracy:.4f} using seed: {random_seed}')


if __name__ == '__main__':
    # Run training once and exit
    train_and_save_model()
