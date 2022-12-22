import numpy as np
from scipy import signal

def Sectioning(matrix,kopfzeile,G=2.5,c = False): # in dieser Funktion werden die Bereiche nach den Kriterien ausgeschnitten
    # G definierts den Schwellwert für das Ausschnieden anhadn des Spindelstroms
    # c definiert den Ausschneidemodus: False --> nur anhand Spindelstrom, True --> zusätzlich bei der ersten Änderung eines Positionssignals

    Schnitt = []   #In der Variable Schnitt werden alle Schnitte gespeichert

    # Ausschneiden anhand des Spindelstroms
    Pos = kopfzeile.index('Cur_SP')   
    Spindel = abs(matrix[range(0,len(matrix[:,Pos])),Pos])  # Spindelstrom als Kriterium
    b, a = signal.butter(3, 0.005)                          # Filterung zur Glättung
    zi = signal.lfilter_zi(b, a)
    z, _ = signal.lfilter(b, a, Spindel, zi=zi*Spindel[0])  # Tiefpass-filterung des Signals um Störanteile zu minimiren
    counter=0                                               # Counter der verhindert das es mehrere Zuschnitte gibt
    for i in range(len(z)):
        counter=counter-1
        if abs(z[i]-G) <= 0.05 and counter<=0:
            k = int(i)
            Schnitt = np.append(Schnitt,k)
            counter = 50
    if z[int(Schnitt[0])+10]<G:                             #Sicherstellen das wir in einem Einschaltbereich sind
         np.delete(Schnitt,0)

    Bereich = []
    for i in range(int(len(Schnitt)/2)):
        Bereich.append([int(Schnitt[i*2]), int(Schnitt[i*2+1])])   #Liste aus Bereichen

    # Ausschneiden Anhand der X-/Y-/Z- Signale anhand der Suche einer Geschwindigkeitszunahme wenn an der Ausschneidstelle des Spindelstroms die Geschwindigkeit gering war
    if c:
        sw = 0.01   # Schwellwert für den Bewreich einer hohen Geschwindigkeit
        diffx = signal.medfilt(abs(np.diff(matrix[:,kopfzeile.index('Pos_X')])),11)
        diffy = signal.medfilt(abs(np.diff(matrix[:,kopfzeile.index('Pos_Y')])),11)
        diffz = signal.medfilt(abs(np.diff(matrix[:,kopfzeile.index('Pos_Z')])),11)

        for i in range(len(Bereich)):
            Bereichweite=int((abs(Bereich[i][0]-Bereich[i][1]))/2)

            # Suche nach dem Start des Abschnitts (Erste Änderung einer konstanten Achse)
            for j in range(Bereichweite):
        
                Stelle = Bereich[i][0]-j
                  
                if Stelle <= 0:
                    break
                if (diffx[Bereich[i][0]] <= sw and diffx[Stelle] > sw) or (diffy[Bereich[i][0]] <= sw and diffy[Stelle] > sw) or (diffz[Bereich[i][0]] <= sw and diffz[Stelle] > sw):
                     Bereich[i][0] = int(Stelle)
                     break

            # Suche nach dem Ende des Abschnitts (Erste Änderung einer konstanten Achse)
            for j in range(Bereichweite):
                Stelle = Bereich[i][1]+j
                if Stelle >= len(matrix) - 1:
                    break
                if (diffx[Bereich[i][1]] <= sw and diffx[Stelle] > sw) or (diffy[Bereich[i][1]] <= sw and diffy[Stelle] > sw) or (diffz[Bereich[i][1]] <= sw and diffz[Stelle] > sw):
                    Bereich[i][1] = int(Stelle)
                    break

    return Bereich