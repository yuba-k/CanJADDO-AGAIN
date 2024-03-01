# -*- coding: utf-8 -*-
#ゴール後ブザーを鳴らしゴールを周知する
import RPi.GPIO as GPIO
import time

buzz=12

tempo = 146
note_length = 60/tempo

pitch_dic = {
        'A#3': 233.1,   'B3': 246.9,    'C4': 261.6,
        'C#4': 277.2,   'D4': 293.7,    'D#4': 311.1,
        'E4': 329.6,    'F4': 349.2,    'F#4': 370.0,
        'G4': 392.0,    'G#4': 415.3,   'A4': 440.0,
        'A#4': 466.2,   'B4': 493.9,    'C5': 523.3,
        'C#5': 554.4,   'D5': 587.3,    'D#5': 622.3,
        'E5': 659.3,    'F5': 698.5,    'F#5': 740.0,
        'G5': 783.991,  'G#5': 830.6,   'A5': 880.0,
        'A#5': 932.3,   'B5': 987.8,    'C6': 1046.5,
        'C#6': 1108.7,  'D6': 1174.7,   'D#6': 1244.5,
        'E6': 1318.5,   'F6': 1396.9,   'F#6': 1480.0,
        'G6': 1568.0,   'G#6': 1661.2,  'A6': 1760.0,
        'A#6': 1864.7,  'B6': 1975.5,   'C7': 2093.0
    }
duration_dic = {
    'whole': 1,            'half' : 0.5, 
    'one-third' : 1/3,     'quarter' : 0.25,
}

def buzz():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzz,GPIO.OUT)
    global buzzer
    buzzer=GPIO.PWM(buzz,523)
    buzzer.start(0)
    time.sleep(1)
    buzzer.ChangeDutyCycle(50)
    ##########################

    coard('C4', 'G4', 'one-third')
    coard('E4', 'C5', 'one-third')
    coard('G4', 'E5', 'one-third')
    coard('C5', 'G5', 'one-third')
    coard('E5', 'C6', 'one-third')
    coard('G5', 'E6', 'one-third')
    coard('E6', 'G6', 'whole')
    coard('C6', 'E6', 'whole')
    coard('C4', 'G#4', 'one-third')
    coard('D#4', 'C5', 'one-third')
    coard('G#4', 'D#5', 'one-third')
    coard('C5', 'G#5', 'one-third')
    coard('D#5', 'C6', 'one-third')
    coard('G#5', 'D#6', 'one-third')
    coard('D#6', 'G#6', 'whole')
    coard('C6', 'D#6', 'whole')
    coard('D4', 'A#4', 'one-third')
    coard('F4', 'D5', 'one-third')
    coard('A#4', 'F5', 'one-third')
    coard('D5', 'A#5', 'one-third')
    coard('F5', 'D6', 'one-third')
    coard('A#5', 'F6', 'one-third')
    coard('F6', 'A#6', 'whole')
    coard('D6', 'A#6', 'one-third')
    coard('D6', 'A#6', 'one-third')
    coard('D6', 'A#6', 'one-third')
    coard('C6', 'C7', 'whole')
        
def note(pitch, duration):
    buzzer.ChangeFrequency(pitch_dic[pitch])
    time.sleep(note_length * duration)
    
def rest(duration):
    buzzer.ChangeDutyCycle(0)
    time.sleep(note_length * duration)
    buzzer.ChangeDutyCycle(50)
    
def coard(pitch1, pitch2, duration):
    count = 0
    while True:
        buzzer.ChangeFrequency(pitch_dic[pitch1])
        time.sleep(0.02)
        buzzer.ChangeFrequency(pitch_dic[pitch2])
        time.sleep(0.02)
        count += 1
        if(note_length * duration <= count*0.06):
            break
    
def coard(pitch1, pitch2, pitch3, duration):
    count = 0
    while True:
        buzzer.ChangeFrequency(pitch_dic[pitch1])
        time.sleep(0.02)
        buzzer.ChangeFrequency(pitch_dic[pitch2])
        time.sleep(0.02)
        buzzer.ChangeFrequency(pitch_dic[pitch3])
        time.sleep(0.02)
        count += 1
        if(note_length * duration <= count*0.06):
            break