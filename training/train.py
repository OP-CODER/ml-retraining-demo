import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from prometheus_client import Gauge
import os
import random

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
    
    # Save model
    os.makedirs('model', exist_ok=True)
    joblib.dump(model, 'model/logistic_regression.joblib')
    
    # Save metrics to file for Streamlit app
    with open('model/metrics.txt', 'w') as f:
        f.write(f'Accuracy: {accuracy:.4f}\n')
        f.write(f'Random seed used for split: {random_seed}\n')
    
    print(f'Model trained with accuracy: {accuracy:.4f} using seed: {random_seed}')

if __name__ == '__main__':
    # Run training once and exit
    train_and_save_model()
