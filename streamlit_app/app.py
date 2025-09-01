import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time
import json
import pandas as pd

# Jenkins configuration
JENKINS_URL = 'http://10.243.238.147:8080'
JOB_NAME = 'ml-retraining-demo'
USER = 'admin'
API_TOKEN = '11406250be19d6c226692b67dc78f17b14'  # Replace with your Jenkins API token


# ---- Jenkins Helper Functions ----
def get_crumb():
    """Fetch CSRF crumb from Jenkins"""
    crumb_url = f"{JENKINS_URL}/crumbIssuer/api/json"
    response = requests.get(crumb_url, auth=HTTPBasicAuth(USER, API_TOKEN))
    if response.status_code == 200:
        crumb_data = response.json()
        return {crumb_data['crumbRequestField']: crumb_data['crumb']}
    else:
        st.error(f"Failed to get Jenkins crumb: {response.status_code}")
        return None


def trigger_job():
    """Trigger Jenkins job"""
    url = f"{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters"
    headers = get_crumb()
    if headers is None:
        return False
    response = requests.post(url, auth=HTTPBasicAuth(USER, API_TOKEN), headers=headers)
    if response.status_code in [200, 201, 202, 302]:
        return True
    else:
        st.error(f"Failed to trigger job: {response.status_code}")
        return False


def get_last_build_status():
    """Check the last Jenkins build status"""
    url = f"{JENKINS_URL}/job/{JOB_NAME}/lastBuild/api/json"
    response = requests.get(url, auth=HTTPBasicAuth(USER, API_TOKEN))
    if response.status_code == 200:
        data = response.json()
        if data['building']:
            return "BUILDING"
        elif data['result'] is None:
            return "PENDING"
        else:
            return data['result']  # SUCCESS, FAILURE, etc.
    return None


def fetch_metrics():
    """Fetch metrics.json artifact from the last successful Jenkins build"""
    url = f"{JENKINS_URL}/job/{JOB_NAME}/lastSuccessfulBuild/artifact/training/metrics.json"
    response = requests.get(url, auth=HTTPBasicAuth(USER, API_TOKEN))

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            st.error("⚠️ Metrics file is not valid JSON. Showing raw response:")
            st.code(response.text[:500])  # Show first 500 chars
            return None
    else:
        st.warning(f"⚠️ metrics.json not found in artifacts. Status code: {response.status_code}")
        return None


# ---- Streamlit UI ----
if 'job_status' not in st.session_state:
    st.session_state.job_status = None
if 'polling' not in st.session_state:
    st.session_state.polling = False

st.title("🚀 ML Model Jenkins Job Control Dashboard")

# Button to trigger Jenkins job
if st.button('▶ Run Jenkins Job') and not st.session_state.polling:
    if trigger_job():
        st.session_state.job_status = "BUILDING"
        st.session_state.polling = True
    else:
        st.error("❌ Failed to trigger Jenkins job.")


# Polling Jenkins job status
if st.session_state.polling:
    status = get_last_build_status()
    if status in ["BUILDING", "PENDING"]:
        st.info("⏳ Job running... please wait.")
        time.sleep(10)
        st.experimental_rerun()
    elif status == "SUCCESS":
        st.success("✅ Job completed successfully! Fetching metrics...")
        st.session_state.job_status = "SUCCESS"
        st.session_state.polling = False

        metrics = fetch_metrics()
        if metrics:
            st.subheader("📊 Model Metrics Summary")

            # Show accuracy
            if "accuracy" in metrics:
                st.metric("Accuracy", f"{metrics['accuracy']:.3f}")

            # Show random seed
            if "random_seed" in metrics:
                st.write(f"**Random seed used:** {metrics['random_seed']}")

            # Show classification report nicely
            if "classification_report" in metrics:
                st.subheader("📑 Classification Report")
                report_df = pd.DataFrame(metrics["classification_report"]).T
                st.dataframe(report_df)

            # Expand to see raw JSON
            with st.expander("🔍 Raw metrics.json"):
                st.json(metrics)
        else:
            st.warning("⚠️ Metrics file not available or invalid.")
    elif status == "FAILURE":
        st.error("❌ Job failed.")
        st.session_state.job_status = "FAILURE"
        st.session_state.polling = False
    else:
        st.warning("⚠️ Unable to get job status.")
        st.session_state.polling = False

# Show last job result if not polling
else:
    if st.session_state.job_status == "SUCCESS":
        st.success("✅ Last job completed successfully.")
        metrics = fetch_metrics()
        if metrics:
            st.subheader("📊 Last Run Metrics")

            if "accuracy" in metrics:
                st.metric("Accuracy", f"{metrics['accuracy']:.3f}")

            if "random_seed" in metrics:
                st.write(f"**Random seed used:** {metrics['random_seed']}")

            if "classification_report" in metrics:
                st.subheader("📑 Classification Report")
                report_df = pd.DataFrame(metrics["classification_report"]).T
                st.dataframe(report_df)

            with st.expander("🔍 Raw metrics.json"):
                st.json(metrics)
    elif st.session_state.job_status == "FAILURE":
        st.error("❌ Last job failed.")
    elif st.session_state.job_status == "BUILDING":
        st.info("⏳ A job is currently running.")
