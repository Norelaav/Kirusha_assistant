import config
import stt
import tts
from fuzzywuzzy import fuzz
import datetime
from num2t4ru import num2text
import webbrowser
import random
import sys
import os
import vosk
import json
import queue
import codecs


'''model = vosk.Model("C:/Users/valer/PycharmProjects/Jarvis/model-small")

samplerate = 16000

q = queue.Queue()
'''



def va_respond(voice: str):
    global vos
    vos = voice
    print(voice)
    if voice.startswith(config.VA_ALIAS):

        cmd = recognize_cmd(filter_cmd(voice))

        if cmd['cmd'] not in config.VA_CMD_LIST.keys():
            tts.va_speak("Что?")
        else:
            execute_cmd(cmd['cmd'])


def filter_cmd(raw_voice: str):
    cmd = raw_voice

    for x in config.VA_ALIAS:
        cmd = cmd.replace(x, "").strip()

    for x in config.VA_TBR:
        cmd = cmd.replace(x, "").strip()

    return cmd


def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in config.VA_CMD_LIST.items():

        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def execute_cmd(cmd: str):
    if cmd == 'help':
        #help
        text = "Я умею: ..."
        text += "произносить время ..."
        text += "рассказывать анекдоты ..."
        text += "и открывать браузер"
        tts.va_speak(text)
        pass
    elif cmd == 'ctime':
        #current time
        now = datetime.datetime.now()
        text = "Сейч+ас " + num2text(now.hour) + " " + num2text(now.minute)
        tts.va_speak(text)

    elif cmd == 'joke':
        jokes = ['Как смеются программисты? ... ехе ехе ехе',
                 'ЭсКьюЭль запрос заходит в бар, подходит к двум столам и спрашивает .. «м+ожно присоединиться?»',
                 'Программист это машина для преобразования кофе в код']

        tts.va_speak(random.choice(jokes))

    elif cmd == 'open_browser':
        #open browser
        webbrowser.open('https://www.youtube.com', new=2)

    elif cmd == 'program_off':
        #program is disabled
        tts.va_speak("Отключаюсь")
        sys.exit()

    elif cmd == 'pc_off':
        tts.va_speak("Всего хорошего, босс")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif cmd == 'read_todo_list':
        pass

    elif cmd == 'add_in_todo_list':
        tts.va_speak("Что добавить в список?")


        #stt.va_listen(va_respond)
        #stt.va_listen(rec)
        '''i = 0
        rec = vosk.KaldiRecognizer(model, samplerate)
        while i == 0:
            if rec.Result() == {"text": ""}:
                pass
            else:
                i += 1'''
        #rec = vosk.KaldiRecognizer(model, samplerate)

        '''data = stt.q.get_nowait()
        if stt.rec.AcceptWaveform(data):'''
        with open('todo_list.txt', 'a', encoding='utf-8') as file:
            file.write(vos)




