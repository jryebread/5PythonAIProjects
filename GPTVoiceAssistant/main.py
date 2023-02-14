import time

import whisper
import boto3
import os
from dotenv import load_dotenv
load_dotenv()
from playsound import playsound
import sounddevice as sd
from scipy.io.wavfile import write
import openai
from pydub import AudioSegment
import requests
import json

fs = 44100  # Sample rate
seconds = 3  # Duration of recording
print(sd.default.device)
sd.default.device = (5, 20)
print(sd.query_devices())
print(sd.default.device)

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')

AWS_ACCESS = os.getenv('AWS_ACCESS')
AWS_SECRET = os.getenv('AWS_SECRET')
LEAP_KEY = os.getenv('LEAP_KEY')
MODELID = "8b1b897c-d66d-45a6-b8d7-8e32421d02cf"

def get_edit_job(inf_id):
    print(inf_id)
    url = f"https://api.leapml.dev/api/v1/images/edit/{inf_id}"
    headers = {"accept": "application/json",
               "authorization": "Bearer {}".format(LEAP_KEY)
               }

    response = requests.get(url, headers=headers)
    if response.text == "": print("AHH")
    return response.json()

def get_single_inf(inf_id):
    print(inf_id)
    url = "https://api.leapml.dev/api/v1/images/models/{}/inferences/{}"\
        .format(MODELID, inf_id)
    print(url)
    headers = {"accept": "application/json",
               "authorization": "Bearer {}".format(LEAP_KEY)
               }

    response = requests.get(url, headers=headers)

    print(response.text)
    if response.text == "": print("AHH")
    return response.json()

def generate_image(prompt):
    url = "https://api.leapml.dev/api/v1/images/models/8b1b897c-d66d-45a6-b8d7-8e32421d02cf/inferences"

    payload = {
        "prompt": prompt,
        "steps": 30,
        "width": 512,
        "height": 512,
        "numberOfImages": 1,
        "seed": 4523184
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer {}".format(LEAP_KEY)
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())
    id = response.json()["id"]
    return f"https://api.leapml.dev/api/v1/images/models/{MODELID}/inferences/{id}"



def submitEditJob(fileName, prompt):

    url = f"https://api.leapml.dev/api/v1/images/edit"
    data = {
        "prompt": prompt,
        "imageGuidanceScale": 2,
        "textGuidanceScale": 16,
        "steps": 50,
    }
    files = {
        "files": (fileName, open(fileName, "rb"), "image/jpeg"),
        "body": (None, json.dumps(data), "application/json"),
    }
    headers = {
        "accept": "application/json",
        "authorization": "Bearer {}".format(LEAP_KEY)
    }

    response = requests.post(url, files=files, headers=headers).json()
    print(response)
    id = response["id"]
    return url + f"/{id}"

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

def recordAudio():
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    write('output.wav', fs, myrecording)  # Save as WAV file
    print("DONE!")

# model = whisper.load_model("base")
# print("Listening to audio...")
# recordAudio()
#
# result = model.transcribe("C:/Users/James/PycharmProjects/5Projects/GPTVoiceAssistant/output.wav")
# print(result)
# print(result["text"])
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer {}".format(LEAP_KEY)
}
# #generate image, get job id
# urlGen = generate_image("amongus character dancing fortnite")
# res = wait(urlGen, headers, "state")
#
# #get inf job completion (DONE)
# infJob = get_single_inf(res["id"])
# print(infJob)
# img_data = requests.get(infJob["images"][0]["uri"]).content
# with open('amogus.jpg', 'wb') as handler:
#     handler.write(img_data)

# edit image
editPrompt = input("Enter edit request: ")
editURL = submitEditJob(fileName="amogus.jpg", prompt=editPrompt)
editRes = wait(editURL, headers, "status")
print("editres: ", editRes)

#get inf job completion
edit = get_edit_job(editRes["id"])
print(edit)









