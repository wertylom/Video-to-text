import whisper
import requests
import os
import torch
from rich import print
from rich.console import Console
import ffmpeg
from pynput import keyboard
from time import sleep
from threading import Thread

console = Console()




if __name__ == '__main__':


###################SPEECH_TO_TEXT###############################


    def DetectLanguage(audioPath):
        model = whisper.load_model("base")

        audio = whisper.load_audio(audioPath)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        _, probs = model.detect_language(mel)

        language = max(probs, key=probs.get)

        return language

    def STTS(audioFile,yes): #Speech To Text Single
        global stop

        stop = False

        inputDir = "./audio/"
        device = "cuda" if torch.cuda.is_available() else "cpu" 
        model = whisper.load_model("turbo", device=device)
        if device == "cuda":
            for p in model.parameters():
                p.data = p.data.float()
        print("Searching for",audioFile)
        if audioFile:
                
                Thread(target = loading).start()

                print("Found",audioFile,"Converting")
                result = model.transcribe(inputDir+audioFile,fp16=False)
                stop = True
                WriteToTxt(result["text"],audioFile)

                if yes : summariseText(result["text"],audioFile)
        else:
            print("Error try could not find specified file")


    def WriteToTxt(text,fileName):
        textDir = "./transcriptions/"
        if "." in fileName:
            fileList = fileName.split(".",1)
            TextFile = open(textDir+fileList[0]+".txt","a",encoding="utf-8")
        else:
            TextFile = open(textDir+fileName+".txt","a",encoding="utf-8")
        TextFile.write(text+"\n")
        folder_path = os.path.abspath("transcriptions").replace("\\", "/")
        console.print(
            f"All saved to txt in [hot_pink2][link=file:///{folder_path}]-->transcriptions<--[/link][/hot_pink2] folder"
        )


###################AI_IMPLEMENTATION############################


    def summariseText(text,fileName):
        console.print
        try:
            response = requests.post(
        "http://localhost:2137/api/v1/chat",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "model": "google/gemma-3-12b",
            "input": f"{text}"
        }
        )
        except:
            console.print("########  Failed to connect to server  ########",style="red3",justify="center")
            return
        if "." in fileName:
            fileList = fileName.split(".",1)
            After_AI = fileList[0]  + "_AfterAI"
        else:
            After_AI = fileName + "_AfterAI"
        if response:
            WriteToTxt(response.json()["output"][0]["content"],After_AI)
            print(response.json()["output"][0]["content"])


###################VIDEO_TO_AUDIO##########################


    def VTAS(fileName): #Video To Audio Single
        inputDir = "./video/"
        outputDir = "./audio/"
        if fileName:
            print("Found",fileName,"Converting")
            fileList = fileName.split(".",1)
            input_file = ffmpeg.input(inputDir+fileName)
            input_file.output(outputDir+fileList[0]+".mp3", 
                                acodec='mp3',
                                loglevel="quiet").run(overwrite_output=True)
            print("Succesfully created audio file go to output to get your file",fileName)
        else:
            print("Could not find ",fileName,"please try again")

    def VTAA(): #Video To Audio All
        mainDir = "./video"
        inputDir = "./video/"
        outputDir = "./audio"
        for file in os.listdir(mainDir):
            if file.endswith((".mp4",".avi")):
                print("Found",file,"Converting")
                fileList = file.split(".",1)
                input_file = ffmpeg.input(inputDir+file)
                input_file.output(outputDir+fileList[0]+".mp3", 
                                acodec='mp3',
                                loglevel="quiet").run(overwrite_output=True)
                

########################MENU###############################


    def loading():
        global stop
        # spiners = "⢎⡰","⢎⡡","⢎⡑","⢎⠱","⠎⡱","⢊⡱","⢌⡱","⢆⡱"
        # spiners = '▁','▃','▄','▅','▆','▇','█','▇','▆','▅','▄','▃'

        spiners = "( ●    )","(  ●   )","(   ●  )","(    ● )","(     ●)","(    ● )","(   ●  )","(  ●   )","( ●    )","(●     )"

        # spiners = "▱▱▱▱▱▱▱","▰▱▱▱▱▱▱","▰▰▱▱▱▱▱","▰▰▰▱▱▱▱","▰▰▰▰▱▱▱","▰▰▰▰▰▱▱","▰▰▰▰▰▰▱","▰▰▰▰▰▰▰"
        huh = 0
        while stop == False:
            print(spiners[huh],end='\r')
            huh+=1
            if huh == len(spiners):
                huh = 0
            sleep(0.1)

    def Menu():
        global btnsList, videoLst, audioLst, selected, selectedMenu, yes

        selectedMenu = 0
        selected = 0


        yes = False #If True sends output of audio to text to AI


        btnsList = [
            {"name": "take audio from video files", "select": True},
            {"name": "take text from audio files", "select": False},
            {"name": "Exit program", "select": False},
        ]

        def draw(lst, text):
            os.system("cls")
            print(text)
            for item in lst:
                icon = ">" if item["select"] else " "
                console.print(icon + item["name"],
                            style="green1" if item["select"] else "purple4")

        def buildVideoList():
            global videoLst
            files = os.listdir("./video")
            videos = [video for video in files if 
                        video.endswith((".mp4",".avi"))]
            videoLst = [{"name": video, "select": False} 
                        for video in videos]
            videoLst.append(
                {"name": "Convert all video files to audio ones", "select": False}
                )
            videoLst.append(
                {"name": "Go back"
                                , "select": False}
                )
            if videoLst:
                videoLst[0]["select"] = True

        def buildAudioList():
            global audioLst
            files = os.listdir("./audio")
            audios = [a for a in files if a.endswith(".mp3")]
            audioLst = [{"name": a, "select": False} for a in audios]
            audioLst.append({"name": "Go back", "select": False})
            if audioLst:
                audioLst[0]["select"] = True

        def move(delta, lst):
            global selected
            lst[selected]["select"] = False
            selected = max(0, min(selected + delta, len(lst) - 1))
            lst[selected]["select"] = True

        def on_press(key):
            global selectedMenu, selected,yes
            lst = (  btnsList if selectedMenu == 0 
                else videoLst if selectedMenu == 1 
                else audioLst)
            text = ("wsg what you wanna do?" if selectedMenu == 0 else
                    "what video to convert?" if selectedMenu == 1 else
                    "what audio to convert?")

            if key == keyboard.Key.up:
                move(-1, lst)
                draw(lst, text)

            elif key == keyboard.Key.down:
                move(1, lst)
                draw(lst, text)

            elif key == keyboard.Key.enter:
                if selectedMenu == 0:
                    if selected == 0:
                        selectedMenu = 1
                        selected = 0
                        buildVideoList()
                        draw(videoLst, "what video to convert?")
                    elif selected == 1:
                        selectedMenu = 2
                        selected = 0
                        buildAudioList()
                        draw(audioLst, "what audio to convert?")
                    elif selected == 2:
                        exit()
                elif selectedMenu == 1:
                    if videoLst[selected]["name"] == "Go back":
                        selectedMenu = 0
                        selected = 0
                        draw(btnsList, "wsg what you wanna do?")
                    elif videoLst[selected]["name"] == "Convert all video files to audio ones":
                        VTAA()
                    else:
                        VTAS(videoLst[selected]["name"])
                elif selectedMenu == 2:
                    if audioLst[selected]["name"] == "Go back":
                        selectedMenu = 0
                        selected = 0
                        draw(btnsList, "wsg what you wanna do?")
                    else:
                        Thread(
                            target = STTS,
                            args=(audioLst[selected]["name"],yes)).start()

            elif key == keyboard.Key.esc:
                exit()

        draw(btnsList, "wsg what you wanna do?")
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    Menu()