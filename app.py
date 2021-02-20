from pytube import YouTube #Korišćenje pztube biblioteke
from moviepy.editor import * #Korišćenje moviepy biblioteke
import os, shutil #Korišćenje os modula za brisanje fajlova
from flask import Flask, render_template, request #Korišćenje Flask frejmvorka
import speech_recognition as sr #Korišćenje SpeechRecognition biblioteke

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    #transcript - Promenljiva u kojoj će se staviti tekst dobijen sa YouTube snimka
    transcript=""

    #U html-u se koristi POST metoda za uzimanje unetog linka videa iz forme
    if request.method == "POST":
        print("Form data received")

        #url - promenljiva u kojoj ce se staviti link YouTube videa iz forme
        url=""

        #Putem flaks-a, koristi se Request objekat i uzima se podatak o url-u YouTube videa iz forme 
        url = request.form["url"]
        
        #Ako url postoji tj. korisnik nije ostavio polje za unos linka prazno... 
        if url:
            #try se koristi zbog moguće greške prilikom učitavanja YouTube url-a u slučaju kada prosleđen url nije link od YouTube-a ili video ne postoji
            try:
                #Koristi se importovan objekat YouTube (iz biblioteke moviepy) kako bi se skinuo video YouTube linka koji je korisnik uneo
                mp4 = YouTube(url).streams.get_highest_resolution().download() 
                #Skinut .mp4 fajl se zatim pretvara u .wav fajl (Specifično .wav a ne .mp3 jer SpeechRecognition biblioteka radi sa .wav fajlovima ali ne i sa .mp3)
                wav = mp4.split(".mp4",1)[0] + ".wav"

                video_clip = VideoFileClip(mp4)
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(wav)

                audio_clip.close()
                video_clip.close()

                #Nakon kreiranja .wav fajla, putem imortovanog os modula, birše se prvobitno skinut .mp4 video  
                os.remove(mp4)

                #Korišćenje Recognizer klase iz importovane SpeechRecognition biblioteke
                recognizer = sr.Recognizer()

                with sr.AudioFile(wav) as source:
                    #Ovde recongnizer priprema .wav fajl za najbolje moguće prevođenje iz govora u tekst
                    recognizer.adjust_for_ambient_noise(source)
                    #U promenljivu audio smešta se snimljen .wav fajl i on predstavlja jedan AudioData objekat
                    audio = recognizer.record(source)
                    #Ako je pretvaranje audia u tekst uspešno, u promenljivu transcript će biti ubačen prepoznat tekst
                    try:
                        print("Converting Audio File To Text...")
                        #Ovde se poziva Google Web Speech API radi prevođenja govora u tekst
                        transcript = recognizer.recognize_google(audio)
                    except:
                        transcript = "Sorry, transcription failed."
                #Na samom kraju, briše se i .wav faj korišćen za prevođenje
                os.remove(wav)

            #Ovo je izuzetak kada nije poslat link sa YouTube-a  ili video YouTube linka ne može da se pusti
            except:
                transcript = "Sorry, no video found."
            
    #Index.html-u se šalje promenljiva transcript kao vrednost istoimene promenljive koja se nalazi u html-u
    #U slučaju da korisnik nije uneo link a kliknuo je dugme za prevođenje, kod promenljive transcript ostaje vrednost praznog stringa pa se to i šalje html-u
    return render_template('index.html', transcript=transcript)

if __name__=="__main__":
    app.run(debug=True, threaded=True)