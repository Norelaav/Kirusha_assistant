import config
import stt
import tts
from fuzzywuzzy import fuzz
import datetime
from num2t4ru import num2text
import webbrowser
import random
import sys
from skills import *


print(f"{config.VA_NAME} (v{config.VA_VER}) начал свою работу ...")
tts.va_speak("Приветствую, босс!")


#начать прослушивание команд
stt.va_listen(va_respond)