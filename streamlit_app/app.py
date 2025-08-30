import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time

JENKINS_URL = 'http://localhost:8080'
JOB_NAME = 'ml-retraining-demo'
USER = 'admin'
API_TOKEN = '1193221706f44c4de96c269d2982546ade'  # Replace with your Jenkins API token

st.title("ML Model Jenkins Job Control Dashboard")

# Sidebar environment selector
env_option = st.sidebar.selectbox("Select Deployment Environment", ['LOCAL', 'EKS'])

def get_crumb():
    crumb_url = f"{JENKINS_URL}/crumbIssuer/api/json"
    response = requests.get(crumb_url, auth=HTTPBasicAuth(USER, API_TOKEN))
    if response.status_code == 200:
        crumb_data = response.json()
        return {crumb_data['crumbRequestField']: crumb_data['crumb']}
    else:
        st.error(f"Failed to get Jenkins crumb: {response.status_code}")
        return {}

def trigger_job():
    url = f"{JENKINS_URL}/job/{JOB_NAME}/build"
    headers = get_crumb()
    response = requests.post(url, auth=HTTPBasicAuth(USER, API_TOKEN), headers=headers)
    if response.status_code == 201:
        return True
    else:
        st.error(f"Failed to trigger job: {response.status_code}")
        return False

def get_last_build_status():
    url = f"{JENKINS_URL}/job/{JOB_NAME}/lastBuild/api/json"
    response = requests.get(url, auth=HTTPBasicAuth(USER, API_TOKEN))
    if response.status_code == 200:
        data = response.json()
        if data['building']:
            return "BUILDING"
        else:
            return data['result']
    else:
        return None

job_triggered = st.button('Run Jenkins Job')

if job_triggered:
    if trigger_job():
        st.info("Job triggered. Waiting for completion...")
        while True:
            status = get_last_build_status()
            if status == "BUILDING":
                st.info("Job running...")
                time.sleep(10)
                st.experimental_rerun()
            elif status == "SUCCESS":
                st.success("Job completed successfully! Showing metrics...")
                # TODO: Fetch and display metrics here
                break
            elif status == "FAILURE":
                st.error("Job failed.")
                break
            else:
                st.warning("Unable to get job status.")
                break
else:
    status = get_last_build_status()
    if status == "BUILDING":
        st.info("A job is currently running...")
    elif status == "SUCCESS":
        st.success("Last job completed successfully.")
        # TODO: Optionally show last metrics here
    elif status == "FAILURE":
        st.error("Last job failed.")
