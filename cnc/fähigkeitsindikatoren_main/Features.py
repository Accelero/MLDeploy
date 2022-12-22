import numpy as np

def region_feature(matrix,Bereich,kopfzeile,static_features=[],merkmale_N=6): # Erstellen der Merkmalsvektoren 
    # matrix + Bereiche als übergabe static_features sollen in load_matrix definiert werden merkmale_N gibt an wie viele 
    # variable merkmale verwendet werden sollen bei N>5 wird der Durchschnitt der Spindeldrehzahl sowie die Dauer als Merkmale angehängt

    merkmale = np.zeros((merkmale_N,len(Bereich)))
    for i in kopfzeile: #füllen der Merkmale 1-x,2-y,3-z,4-b,5-mean(Ia)
        if i == 'Pos_X':
            for j in range(len(Bereich)):
                #zurückgelegter Weg in X als Merkmal
                merkmale[0,j] = sum([abs(matrix[k+Bereich[j][0],kopfzeile.index(i)]-matrix[k+Bereich[j][0]+1,kopfzeile.index(i)]) for k in range(int(Bereich[j][1]-Bereich[j][0]-1))])

        if i == 'Pos_Y':
            for j in range(len(Bereich)):
                #zurückgelegter Weg in Y als Merkmal
                merkmale[1,j] = sum([abs(matrix[k+Bereich[j][0],kopfzeile.index(i)]-matrix[k+Bereich[j][0]+1,kopfzeile.index(i)]) for k in range(int(Bereich[j][1]-Bereich[j][0]-1))])

        if i == 'Pos_Z':
            for j in range(len(Bereich)):
                #zurückgelegter Weg in Z als Merkmal
                merkmale[2,j] = sum([abs(matrix[k+Bereich[j][0],kopfzeile.index(i)]-matrix[k+Bereich[j][0]+1,kopfzeile.index(i)]) for k in range(int(Bereich[j][1]-Bereich[j][0]-1))])

        if i == 'Pos_B':
            for j in range(len(Bereich)):
                #zurückgelegter Weg in B als Merkmal
                merkmale[3,j] = sum([abs(matrix[k+Bereich[j][0],kopfzeile.index(i)]-matrix[k+Bereich[j][0]+1,kopfzeile.index(i)]) for k in range(int(Bereich[j][1]-Bereich[j][0]-1))])

        if i == 'Speed_SP':
                for j in range(len(Bereich)):
                    merkmale[4,j] = np.mean(matrix[slice(Bereich[j][0],Bereich[j][1],1),kopfzeile.index(i)])
                    # durchschnittliche Spindeldrehzahl

        if i == 'time':
                for j in range(len(Bereich)):
                    merkmale[5,j] = abs(matrix[Bereich[j][1], kopfzeile.index(i)] - matrix[Bereich[j][0], kopfzeile.index(i)])
                    # Dauer der Aufnahme

    Zuschnitte = []
    for i in range(len(Bereich)):
        Zuschnitte_h =[]
        Zuschnitte_h.extend([static_features,merkmale[:,i], kopfzeile,matrix[np.arange(Bereich[i][0], Bereich[i][1]),:]])
        Zuschnitte.append(Zuschnitte_h)
        # zuschneiden der Matrix und Speichern als Listen
        # Die Zuschnitte werden als liste von listen gespeichert der erste eintrag Z[i][0] ist der statischeMerkmalsvektor der 
        # zweite Eintrag Z[i][1] ist die variable Merkmalsverktor
        # dritte Eintrag Z[i][2] sind die Namen
        # vierte Eintrag Z[i][3] ist die Matrix aus den Messdaten

    return Zuschnitte