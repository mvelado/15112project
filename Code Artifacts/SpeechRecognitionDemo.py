#!/uspeech/bin/env python3

import time
# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as speech


# obtain audio from the microphone
r = speech.Recognizer()
with speech.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)


# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
except speech.UnknownValueError:
    print("I'm sorry! I couldn't understand!")
except speech.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))

