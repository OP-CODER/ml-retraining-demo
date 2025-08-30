import streamlit as st
import subprocess
import os
import sys

# Path to metrics file saved by training script
METRICS_PATH = os.path.join(os.path.dirname(__file__), 'training', 'model', 'metrics.txt')

st.title('ML Model Retraining Dashboard')

def read_metrics():
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'r') as f:
            return f.read()
    return 'No metrics found. Please retrain the model.'

def trigger_retraining():
    st.info('Triggering retraining...')
    # Get absolute path to train.py
    train_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'training', 'train.py'))
    python_exe = sys.executable  # Use current python interpreter (virtual environment)
    try:
        result = subprocess.run([python_exe, train_py_path],
                                capture_output=True, text=True, check=True)
        st.success('Retraining completed successfully!')
        st.text('Output:\n' + result.stdout)
    except subprocess.CalledProcessError as e:
        st.error(f'Retraining failed with error:\n{e.stderr}')

if st.button('Trigger Model Retraining'):
    trigger_retraining()

st.subheader('Latest Model Metrics:')
st.text_area('Metrics', read_metrics(), height=100)

st.write('Please refresh the page manually to see latest metrics.')
