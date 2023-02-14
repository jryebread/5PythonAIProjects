import streamlit as st
import pandas as pd
import numpy as np
import whisper
import requests
import time
from PIL import Image
import json
import os
from scipy.io.wavfile import write
from io import BytesIO

st.title('Art Voice Assistant')
st.subheader("Follow [@jamescodez](https://twitter.com/jamescodez) on twitter for updates")
LEAP_KEY = os.getenv('LEAP_KEY')
MODELID = "8b1b897c-d66d-45a6-b8d7-8e32421d02cf"

import streamlit as st
from audio_recorder_streamlit import audio_recorder

def wait(resUrl, headers, state):
    while True:
        resultResponse = requests.get(resUrl, headers=headers).json()
        print("resWait: ", resultResponse)
        if resultResponse[state] == 'finished':
            print(resultResponse)
            return resultResponse
        if resultResponse[state] == 'failed':
            print("The edit job failed")
            break
        if resultResponse[state] == 'processing':
            print("The edit job is processing")
        if resultResponse[state] == 'queued':
            print("The edit job is queued")
        time.sleep(3)


edit_url = f"https://api.leapml.dev/api/v1/images/edit"

headers = {
    "accept": "application/json",
    "authorization": f"Bearer " # ADD YOUR BEARER TOKEN TODO!
}
def submitEditJob(prompt):

    url = f"https://api.leapml.dev/api/v1/images/edit"
    files = {
        "files": ("img.jpg", open("img.jpg", "rb"), "image/jpeg"),
    }

    payload = {
        "prompt": prompt,
        "imageGuidanceScale": "2",
        "textGuidanceScale": "19",
        "steps": "25",
    }

    response = requests.post(url, data=payload, files=files, headers=headers).json()
    print(response)
    id = response["id"]
    return url + f"/{id}"


imgBytes = None
# upload image to streamlit
uploaded_file = st.file_uploader("Choose a image", type=["png", "jpg", "jpeg"])
print("Uploaded file: ", uploaded_file)
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.image(bytes_data)
    imgBytes = bytes_data
    with open('img.jpg', 'wb') as handler:
        handler.write(imgBytes)

audio_bytes = audio_recorder()


def get_edit_job(id):
    print(id)
    url = f"https://api.leapml.dev/api/v1/images/edit/{id}"

    response = requests.get(url, headers=headers)
    return response.json()



if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    with open("whisper.wav", 'wb') as f:
        f.write(audio_bytes)
    model = whisper.load_model("base")
    print("Listening to audio...")

    result = model.transcribe("C:/Users/James/PycharmProjects/5Projects/GPTVoiceAssistant/whisper.wav")
    print(result)
    print(result["text"])
    headers = {
        "accept": "application/json",
        "authorization": "Bearer " # ADD BEARER TOKEN TODO!
    }

    # edit image job
    edit_result = submitEditJob(prompt=result["text"])

    edit_res = wait(edit_result, headers, "status")

    #load image from result
    print("FINAL", edit_res["editedImageUri"])
    print(edit_res["editedImageUri"])
    im = Image.open(requests.get(edit_res["editedImageUri"], stream=True).raw)

    st.image(im)

