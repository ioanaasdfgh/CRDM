import Adafruit_ADS1x15  # Importam biblioteca Adafruit_ADS1x15
#Adafruit ofera libraria CircuitPython
import serial  # Importam biblioteca serial
import time #Se importa functiile asociate timpului, acces si conversii

rate = [0]*10  # Initializam un tablou cu 10 elemente, toate setate la 0
amp = 100  # Variabila pentru amplitudine
GAIN = 2/3  # Valoarea de amplificare a semnalului
curState = 0  # Starea curenta
stateChanged = 0  # Indicator pentru schimbarea starii

ser = serial.Serial("/dev/ttyS0", 9600)  # Initializam portul serial

def send_to_processing(prefix, data):
    ser.write(prefix.encode())  # Trimite prefixul catre portul serial
    ser.write(str(data).encode())  # Trimite datele catre portul serial
    ser.write("\n".encode())  # Trimite un caracter newline pentru a marca sfarsitul datelor

def read_pulse():
    firstBeat = True  #Aceasta variabila este un indicator care arata daca a avut loc prima bataie
    secondBeat = False #Aceasta variabila este un indicator care arata daca a avut loc a doua bataie
    sampleCounter = 0 #Aceasta variabila este pentru numarul de esantioane
    lastBeatTime = 0 #Aceasta variabila stocheaza timpul pt bataia anterioare
    lastTime = int(time.time()*1000) #Aceasta variabila stocheaza timpul curent in milisecunde
    th = 525 #Aceasta variabila reprezinta valoarea pragului pentru semnalul cardiac
    P = 512 #Aceasta variabila stocheaza valoarea maxima a semnalului cardiac
    T = 512 #Aceasta variabila stocheaza valoarea minima a semnalului cardiac
    IBI = 600 #Intervalul interbeat, timpul dintre 2 batai consecutive
    Pulse = False #Aceasta variabila este un indicator care arata daca se detecteaza o bataie
    adc = Adafruit_ADS1x15.ADS1015()  # Initializam CAD

    while True:
        Signal = adc.read_adc(0, gain=GAIN)  # Citeste valoarea semnalului de la ADC
        curTime = int(time.time()*1000)
        send_to_processing("S", Signal)  # Trimite semnalul catre procesare in Processing
        sampleCounter += curTime - lastTime
        lastTime = curTime
        N = sampleCounter - lastBeatTime

        if Signal > th and Signal > P:
            P = Signal

        if Signal < th and N > (IBI/5.0)*3.0:
            if Signal < T:
                T = Signal

        if N > 250:
            if Signal > th and Pulse == False and N > (IBI/5.0)*3.0:
                Pulse = 1
                IBI = sampleCounter - lastBeatTime
                lastBeatTime = sampleCounter

                if secondBeat:
                    secondBeat = 0
                    for i in range(0, 10):
                        rate[i] = IBI

                if firstBeat:
                    firstBeat = 0
                    secondBeat = 1
                    continue

                runningTotal = 0
                for i in range(0, 9):
                    rate[i] = rate[i+1]
                    runningTotal += rate[i]

                rate[9] = IBI
                runningTotal += rate[9]
                runningTotal /= 10
                BPM = 60000/runningTotal
                print("BPM:" + str(BPM))  # Afiseaza frecventa cardiaca calculata (BPM)
                send_to_processing("B", BPM)  # Trimite frecventa cardiaca catre Processing
                send_to_processing("Q", IBI)  # Trimite intervalul R-R catre Processing

        if Signal < th and Pulse == 1:
            amp = P - T
            th =amp/2 + T
            T = th
            P = th
            Pulse = 0

        if N > 2500:
            th = 512
            T = th
            P = th
            lastBeatTime = sampleCounter
            firstBeat = 0
            secondBeat = 0
            print("nu s-a identificat")  # Afiseaza mesajul 

        time.sleep(0.005)

read_pulse()  # Apelul functiei pentru a incepe citirea si procesarea semnalului cardiac, citirea continua a semnalului cardiac, detectarea bataielor si calcularea IBI si frecventei cardiace