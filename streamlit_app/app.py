import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time

JENKINS_URL = 'http://192.168.56.1:8080'  # Use this if running in Docker to connect to host Jenkins
JOB_NAME = 'ml-retraining-demo'
USER = 'admin'
API_TOKEN = '11406250be19d6c226692b67dc78f17b14'  # Update with your Jenkins API token

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
    url = f"{JENKINS_URL}/job/{JOB_NAME}/buildWithParameters"
    headers = get_crumb()
    response = requests.post(url, auth=HTTPBasicAuth(USER, API_TOKEN), headers=headers)
    if response.status_code in [200, 201, 302]:
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
    return None

if 'job_status' not in st.session_state:
    st.session_state.job_status = None
if 'polling' not in st.session_state:
    st.session_state.polling = False

st.title("ML Model Jenkins Job Control Dashboard")

if st.button('Run Jenkins Job') and not st.session_state.polling:
    if trigger_job():
        st.session_state.job_status = "BUILDING"
        st.session_state.polling = True
    else:
        st.error("Failed to trigger Jenkins job.")

if st.session_state.polling:
    status = get_last_build_status()
    if status == "BUILDING":
        st.info("Job running... please wait.")
        time.sleep(10)
        st.rerun()
    elif status == "SUCCESS":
        st.success("Job completed successfully! Showing metrics...")
        st.session_state.job_status = "SUCCESS"
        st.session_state.polling = False
        # TODO: Fetch and display metrics here
    elif status == "FAILURE":
        st.error("Job failed.")
        st.session_state.job_status = "FAILURE"
        st.session_state.polling = False
    else:
        st.warning("Unable to get job status.")
        st.session_state.polling = False
else:
    if st.session_state.job_status == "SUCCESS":
        st.success("Last job completed successfully.")
        # TODO: Optionally show last metrics here
    elif st.session_state.job_status == "FAILURE":
        st.error("Last job failed.")
    elif st.session_state.job_status == "BUILDING":
        st.info("A job is currently running...")
