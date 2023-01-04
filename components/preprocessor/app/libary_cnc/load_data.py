import numpy as np
import csv

def load_matrix(data_name,number_static_features=0): 
    # diese Funktion lädt die Datein aus der csv datei als Eingabe wird der Dateipfad erwartet

    f_Sample = 500   # Aufnahmefrequenz

    with open(data_name, 'r', encoding='utf-8') as csv_datei:
        reader = csv.reader(csv_datei, delimiter = ',')   #E inlesen-der CSV Datei
        kopfzeile = ['time'] + next(reader)   # Abschneiden der ersten Zeile und Speichern als Kopfzeile die wird im Moment noch nicht benutzt
        liste = []
        for row in reader:
            liste.append(row)   # Abspeichern der csv. Daten als Liste

    matrix = np.zeros((len(liste),len(liste[0]) - number_static_features))   # erstellen der Datenmatrix
    static_features = np.zeros((len(liste), number_static_features))   # Anfügen von statischen Features (LF-Data), wird noch nicht benutzt
 
    for i in range(len(liste)):
        matrix[i,:] = liste[i][0:len(liste[0])-number_static_features]   #F Füllen der Datenmatrix
        static_features[i,:] = liste[i][len(liste[0])-number_static_features:]

    time = np.arange(0,len(matrix[:,0])*1/f_Sample, 1/f_Sample)   # Zeit array erstellen

    matrix = np.column_stack([time,matrix])

    return matrix,static_features,kopfzeile