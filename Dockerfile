# Use official Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy all project files to /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports
# 8501 for Streamlit UI, 8000 for Prometheus metrics
EXPOSE 8501 8000

# Command to run both training script (in background) and Streamlit app
CMD ["sh", "-c", "python3 training/train.py & streamlit run streamlit_app/app.py --server.port=8501 --server.address=0.0.0.0"]
