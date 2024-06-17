# main.py

import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import subprocess
from googletrans import Translator
import requests
import re
from config import weather_api_key, news_api_key  # Import API keys from config file

# Initialize the recognizer and the text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
translator = Translator()

# Define the speak function
def speak(text, lang='en'):
    if lang == 'hi':
        translated_text = translator.translate(text, src='en', dest='hi').text
        engine.say(translated_text)
    else:
        engine.say(text)
    engine.runAndWait()

# Define the listen function to recognize both English and Hindi
def listen(language='en-IN'):
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language=language)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not get that.")
            return ""
        except sr.RequestError:
            print("Sorry, the service is down.")
            return ""

# Define a dictionary of known applications and their commands/URLs
app_commands = {
    "camera": "start microsoft.windows.camera:",
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "chrome": "start chrome",
    "firefox": "start firefox",
    "edge": "start msedge",
    "word": "start winword",
    "excel": "start excel",
    "powerpoint": "start powerpnt",
    "spotify": "start spotify",
    "vlc": "start vlc",
    "youtube": "https://www.youtube.com",
    "vscode": "code",
    # Add more applications and websites as needed
}

# Define a dictionary of known applications and their process names for closing
app_processes = {
    "notepad": "notepad.exe",
    "calculator": "Calculator.exe",
    "paint": "mspaint.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "edge": "msedge.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "spotify": "Spotify.exe",
    "vlc": "vlc.exe",
    "vscode": "Code.exe",
    # Add more applications and their process names as needed
}

# Define a function to open applications
def open_application(app_name):
    if app_name in app_commands:
        command = app_commands[app_name]
        if command.startswith("http"):
            webbrowser.open(command)
        else:
            os.system(command)
        speak(f"Opening {app_name}")
    else:
        speak(f"Sorry, I don't know how to open {app_name}")

# Define a function to close applications
def close_application(app_name):
    if app_name in app_processes:
        process_name = app_processes[app_name]
        subprocess.call(["taskkill", "/F", "/IM", process_name])
        speak(f"Closing {app_name}")
    else:
        speak(f"Sorry, I don't know how to close {app_name}")

# Function to get weather information
def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": weather_api_key,
        "units": "metric"  # Use "imperial" for Fahrenheit
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather = data['weather'][0]
        temp = main['temp']
        description = weather['description']
        return f"The current temperature in {city} is {temp}°C with {description}."
    else:
        return "Sorry, I couldn't fetch the weather data."

# Define the main function
def main():
    speak("Hello, how can I assist you today?")
    while True:
        command = listen(language='hi-IN')  # Listen for Hindi commands
        if 'exit' in command:
            speak("Goodbye!", lang='hi')
            break
        elif 'hello' in command:
            speak("Hello! How can I help you?")
        else:
            open_match = re.search(r'open (\w+)', command)
            close_match = re.search(r'close (\w+)', command)
            weather_match = re.search(r'weather in (\w+)', command)
            if open_match:
                app_name = open_match.group(1)
                open_application(app_name)
            elif close_match:
                app_name = close_match.group(1)
                close_application(app_name)
            elif weather_match:
                city = weather_match.group(1)
                weather_info = get_weather(city)
                speak(weather_info)
            else:
                speak("Sorry, I didn't understand that.", lang='hi')

# Ensure the script runs the main function
if __name__ == "__main__":
    main()
