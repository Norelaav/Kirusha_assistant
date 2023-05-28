# КЕША 3.0 (aka Jarvis)
"""
    ВНИМАНИЕ!!!
    Пока что это максимально сырой прототип.
    Позже будет опубликована нормальная версия с удобной установкой и поддержкой всего чего только можно.
    А пока что, код ниже к вашим услугам, сэр :)

    @TODO:
    0. Адекватная архитектура кода, собрать всё и переписать from the ground up.
    1. Задержка воспроизведения звука на основе реальной длительности .wav файла (прогружать при запуске?)
    2. Speech to intent?
    3. Отключать self listening protection во время воспроизведения с наушников.
    4. Указание из списка или по имени будет реализовано позже.
"""

import os
import random

import pvporcupine
import simpleaudio as sa
from pvrecorder import PvRecorder
from rich import print
import vosk
import sys
import queue
import json
import struct
import config
from fuzzywuzzy import fuzz
import tts
import datetime
from num2t4ru import num2text
import subprocess
import time
import webbrowser
from gtts import gTTS
from playsound import playsound

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL, COMObject
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)

import openai
from gpytranslate import SyncTranslator

CDIR = os.getcwd()

# init translator
t = SyncTranslator()

# init openai
openai.api_key = config.OPENAI_TOKEN

# PORCUPINE
porcupine = pvporcupine.create(
    access_key=config.PICOVOICE_TOKEN,
    keyword_paths=["utils/Flora_en_windows_v2_2_0.ppn"],

    #keywords=['hey siri'],

    sensitivities=[1]
)
# print(pvporcupine.KEYWORDS)

# VOSK
model = vosk.Model("model-small")
samplerate = 16000
device = config.MICROPHONE_INDEX
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()


def gpt_answer(message):
    model_engine = "text-davinci-003"
    max_tokens = 128  # default 1024
    prompt = t.translate(message, targetlang="en")
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt.text,
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    translated_result = t.translate(completion.choices[0].text, targetlang="ru")
    return translated_result.text


# play(f'{CDIR}\\sound\\ok{random.choice([1, 2, 3, 4])}.wav')
def play(phrase, wait_done=True):
    global recorder
    filename = f"{CDIR}\\zvuki\\"

    if phrase == "greet": # for py 3.8
        filename += f"great{random.choice([1, 2, 3])}.mp3"
    elif phrase == "hello":
        filename += f"hello{random.choice([1, 2])}.mp3"
    elif phrase == "ok":
        filename += f"ok.mp3"
    elif phrase == "not_found":
        filename += "not_found.wav"
    elif phrase == "thanks":
        filename += "thanks.wav"
    elif phrase == "run":
        filename += "run.wav"
    elif phrase == "stupid":
        filename += "stupid.wav"
    elif phrase == "ready":
        filename += "ready.wav"
    elif phrase == "off":
        filename += f"off{random.choice([1, 2])}.mp3"
    elif phrase == "pc_off":
        filename += "pc_off.mp3"
    if wait_done:
        recorder.stop()

    wave_obj = sa.WaveObject.from_wave_file(filename)
    wave_obj.play()

    if wait_done:
        # play_obj.wait_done()
        # time.sleep((len(wave_obj.audio_data) / wave_obj.sample_rate) + 0.5)
        # print("END")
        time.sleep(0.8)
        recorder.start()


def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def va_respond(voice: str):
    global recorder
    print(f"Распознано: {voice}")

    cmd = recognize_cmd(filter_cmd(voice))

    print(cmd)

    if len(cmd['cmd'].strip()) <= 0:
        return False
    elif cmd['percent'] < 70 or cmd['cmd'] not in config.VA_CMD_LIST.keys():
        # play("not_found")
        # tts.va_speak("Что?")
        if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:
            gpt_result = gpt_answer(voice)
            recorder.stop()
            tts.va_speak(gpt_result)
            time.sleep(1)
            recorder.start()
            return False
        #else:
            #play("not_found")
           # tts.va_speak("Команда не распознана")
         #   time.sleep(1)

        return False
    else:
        execute_cmd(cmd['cmd'], voice)
        return True


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


def execute_cmd(cmd: str, voice: str):
    if cmd == 'help':
        # help
        text = "Я умею: ..."
        text += "произносить время ..."
        text += "рассказывать анекдоты ..."
        text += "и открывать браузер"
        tts.va_speak(text)
        pass
    elif cmd == 'ctime':
        # current time
        now = datetime.datetime.now()
        text = "Сейч+ас " + num2text(now.hour) + " " + num2text(now.minute)
        tts.va_speak(text)

    elif cmd == 'joke':
        jokes = ['Как смеются программисты? ... ехе ехе ехе',
                 'ЭсКьюЭль запрос заходит в бар, подходит к двум столам и спрашивает .. «м+ожно присоединиться?»',
                 'Программист это машина для преобразования кофе в код']

        #play("ok", True)

        tts.va_speak(random.choice(jokes))

    elif cmd == 'open_browser':
        #tts.va_speak("Открываю")
        #webbrowser.open('https://www.youtube.com', new=2)

        #text_sp = "Слушаю"
        #s = gTTS(text=text_sp, lang='ru', slow=False)
        #s.save("ss/good.mp3")
        #playsound('ss/good.mp3')
        play("ok")

        #play("not_found")

        #subprocess.Popen([f'{CDIR}\\custom-commands\\Run browser.exe'])
        #play("ok")

    elif cmd == 'open_youtube':
        webbrowser.open('https://www.youtube.com')
        play("ok")

    elif cmd == 'open_google':
        pass
        #webbrowser.get("google-chrome").open()
        #subprocess.call(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')

    elif cmd == 'music':
        tts.va_speak("Функция не работает")

    elif cmd == 'music_off':
        tts.va_speak("Функция не работает")

    elif cmd == 'music_save':
        tts.va_speak("Функция не работает")

    elif cmd == 'music_next':
        tts.va_speak("Функция не работает")

    elif cmd == 'music_prev':
        tts.va_speak("Функция не работает")

    elif cmd == 'sound_off':
        tts.va_speak("Отключаю звук")

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)

    elif cmd == 'sound_on':
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0, None)

        tts.va_speak("Звук включён")

    elif cmd == 'thanks':
        tts.va_speak("Всегда к вашим услугам")

    elif cmd == 'stupid':
        tts.va_speak("Очень тонкое замечание")

    elif cmd == "off":
        #tts.va_speak("Отключаюсь")
        play("off")
        exit()

    elif cmd == 'pc_off':
        #tts.va_speak("Всего хорошего, босс")
        play("pc_off")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

        porcupine.delete()
        exit(0)


    '''elif cmd == 'gaming_mode_on':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to gaming mode.exe'])
        play("ready")

    elif cmd == 'gaming_mode_off':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch back to workspace.exe'])
        play("ready")

    elif cmd == 'switch_to_headphones':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to headphones.exe'])
        time.sleep(0.5)
        play("ready")

    elif cmd == 'switch_to_dynamics':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to dynamics.exe'])
        time.sleep(0.5)
        play("ready")'''




# `-1` is the default input audio device.
recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
recorder.start()
print('Using device: %s' % recorder.selected_device)

print(f"Jarvis (v3.0) начал свою работу ...")
#play("Привет")
#tts.va_speak("Приветствую, босс")
play("hello")

time.sleep(0.5)

ltc = time.time() - 1000

while True:
    try:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            recorder.stop()
            #play("greet", True)
            #tts.va_speak("Слушаю")
            play("greet", True)
            print("Yes, sir.")
            recorder.start()  # prevent self recording
            ltc = time.time()

        while time.time() - ltc <= 10:
            pcm = recorder.read()
            sp = struct.pack("h" * len(pcm), *pcm)

            if kaldi_rec.AcceptWaveform(sp):
                if va_respond(json.loads(kaldi_rec.Result())["text"]):
                    ltc = time.time()

                break

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
