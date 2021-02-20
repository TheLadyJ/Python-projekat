from pytube import YouTube
from moviepy.editor import *
import os, shutil
from flask import Flask, render_template, request
import speech_recognition as sr

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    #transcript = promenljiva u kojoj ce se staviti tekst dobijen sa yt snimka
    transcript=""

    #u html-u se koristi POST metoda za uzimanje linka yt videa iz forme
    if request.method == "POST":
        print("Form data received")

        #url = promenljiva u kojoj ce se staviti link yt videa iz forme
        url=""

        #importovali smo iz flask-a request pa mozemo da prikupimo link iz forme
        url = request.form["url"]
        
        #ako url postoji tj. korisnik nije ostavio polje za unos linka prazno... 
        if url:
            #try zbog moguce greske prilikom ucitavanja YouTube(url) u slucaju kada prosedjen url nije link od youtube-a ili video ne postoji
            try:
                #importovali smo YouTube iz pytube-a pa mozemo da skinemo video ciji je url korisnik uneo
                mp4 = YouTube(url).streams.get_highest_resolution().download() 
                #pretvaramo taj .mp4 u .wav fajl // SpeechRecognition radi sa .wav fajlovima ali ne i sa .mp3
                mp3 = mp4.split(".mp4",1)[0] + ".wav"

                video_clip = VideoFileClip(mp4)
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(mp3)

                audio_clip.close()
                video_clip.close()

                #(importovali smo os) nakon sto je napravljen audio fajl, video fajl se brise   
                os.remove(mp4)

                recognizer = sr.Recognizer()

                with sr.AudioFile(mp3) as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.record(source)
                    #Ako je pretvaranje audia u tekst uspesno, u promenljivu transcript ce biti ubacen prepoznat tekst
                    try:
                        print("Converting Audio File To Text...")
                        transcript = recognizer.recognize_google(audio)
                    except:
                        transcript = "Sorry, transcription failed."
                os.remove(mp3)
            #Ovo je izuzetak kada nije poslat link sa YouTube-a  ili video yt linka ne moze da se pusti
            except:
                transcript = "Sorry, no video found."
            
    #Ovde se index.html-u salje promenljiva transcript kao vrednost istoimene promenljive koja se nalazi u html-u
    return render_template('index.html', transcript=transcript)

if __name__=="__main__":
    app.run(debug=True, threaded=True)