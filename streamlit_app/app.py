import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time

JENKINS_URL = 'http://localhost:8080'
JOB_NAME = 'ml-retraining-demo'
USER = 'admin'
API_TOKEN = '1193221706f44c4de96c269d2982546ade'
JOB_TOKEN = 'ENKINS_URL/job/ml-retraining-demo/build?token=TOKEN_NAME or /buildWithParameters?token=a1b2c3d4e5'  # configured in Jenkins job trigger

def trigger_job():
    url = f"{JENKINS_URL}/job/{JOB_NAME}/build?token={JOB_TOKEN}"
    response = requests.post(url, auth=HTTPBasicAuth(USER, API_TOKEN))
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
        if data['building']:  # job still running
            return "BUILDING"
        else:
            return data['result']  # SUCCESS or FAILURE
    else:
        return None

if st.button('Run Jenkins Job'):
    if trigger_job():
        st.info("Job triggered. Waiting for completion...")
        while True:
            status = get_last_build_status()
            if status == "BUILDING":
                time.sleep(5)
                st.info("Job running...")
            else:
                if status == "SUCCESS":
                    st.success("Job completed successfully! Showing metrics...")
                    # TODO: Add code to fetch and display metrics here
                else:
                    st.error("Job failed.")
                break
