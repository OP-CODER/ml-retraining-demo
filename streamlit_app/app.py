import streamlit as st
import subprocess
import os
import sys

# Path to metrics file saved by training script
METRICS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'training', 'model', 'metrics.txt')
)

st.title('ML Model Retraining Dashboard')

def read_metrics():
    st.write("DEBUG: Looking for metrics at:", METRICS_PATH)  # 👈 shows exact path
    if os.path.exists(METRICS_PATH):
        st.write("DEBUG: Metrics file FOUND ✅")
        with open(METRICS_PATH, 'r') as f:
            return f.read()
    else:
        st.write("DEBUG: Metrics file NOT FOUND ❌")
    return 'No metrics found. Please retrain the model.'

def trigger_retraining():
    st.info('Triggering retraining...')
    train_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'training', 'train.py'))
    python_exe = sys.executable
    try:
        result = subprocess.run([python_exe, train_py_path],
                                capture_output=True, text=True, check=True)
        st.success('Retraining completed successfully!')
        st.text('Output:\n' + result.stdout)

        # 🔑 Immediately refresh and show metrics after retraining
        st.subheader('Latest Model Metrics:')
        st.text(read_metrics())

    except subprocess.CalledProcessError as e:
        st.error(f'Retraining failed with error:\n{e.stderr}')

if st.button('Trigger Model Retraining'):
    trigger_retraining()
else:
    st.subheader('Latest Model Metrics:')
    st.text(read_metrics())
