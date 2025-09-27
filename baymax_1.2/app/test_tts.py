import pyttsx3

def speak(text: str):
    e = pyttsx3.init()
    rate = e.getProperty("rate")
    e.setProperty("rate", int(rate * 0.95))
    e.say(text)
    e.runAndWait()

if __name__ == "__main__":
    speak("Halo. Mulut Baymax berfungsi.")
