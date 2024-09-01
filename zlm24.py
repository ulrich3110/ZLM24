#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import os
import pandas as pd
import random
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Keys für Lotto-Zahlen
DRAW_ZAHLEN = ['Zahl 1',  'Zahl 2', 'Zahl 3', 'Zahl 4', 'Zahl 5',
               'Zahl 6']
DRAW_ZUSATZ = ['Zusatz-Zahl']
DRAW_TOTAL = []
DRAW_TOTAL.extend(DRAW_ZAHLEN)
DRAW_TOTAL.extend(DRAW_ZUSATZ)
# Keys für Prognose-Zahlen
PROGNOSE_ZAHLEN = ['PredZ1', 'PredZ2', 'PredZ3', 'PredZ4', 'PredZ5',
                   'PredZ6']
PROGNOSE_ZUSATZ = ['PredZZ']
PROGNOSE_TOTAL = []
PROGNOSE_TOTAL.extend(PROGNOSE_ZAHLEN)
PROGNOSE_TOTAL.extend(PROGNOSE_ZUSATZ)
# Keys für Durschnitts-Zahlen
AVG_ZAHLEN = ['AvgZ1', 'AvgZ2', 'AvgZ3', 'AvgZ4', 'AvgZ5', 'AvgZ6']
AVG_ZUSATZ = ['AvgZZ']
AVG_TOTAL = []
AVG_TOTAL.extend(AVG_ZAHLEN)
AVG_TOTAL.extend(AVG_ZUSATZ)
# Keys für Ziel-Zahlen
TARGET_ZAHLEN = ['TrgZ1', 'TrgZ2', 'TrgZ3', 'TrgZ4', 'TrgZ5', 'TrgZ6']
TARGET_ZUSATZ = ['TrgZZ']
TARGET_TOTAL = []
TARGET_TOTAL.extend(TARGET_ZAHLEN)
TARGET_TOTAL.extend(TARGET_ZUSATZ)
# SMA-Grösse
SMA_SIZE = 100


def set_draw():
    ''' Eine Lotto-Ziehung nach Zufall machen '''
    # Anzahl Zahlen und Liste vorbereiten
    len_zahlen = len(DRAW_ZAHLEN)
    zahlen_liste = []
    # Zahlen durchlaufen
    for zahl_nur in range(len_zahlen):
        durchlaufen = True
        while durchlaufen:
            zahl_nur = random.randint(1, 49)
            if zahl_nur in zahlen_liste:
                # Zahl ist brereits vorhanden
                durchlaufen = True
            else:
                # Zahl ist noch nicht vorhanden
                zahlen_liste.append(zahl_nur)
                durchlaufen = False
    # Zahlen sortieren
    zahlen_liste.sort()
    # Anzahl Zusatz Zahlen und Liste vorbereiten
    len_zusatz = len(DRAW_ZUSATZ)
    zusatz_liste = []
    # Zusatz durchlaufen
    for zusatz_nr in range(len_zusatz):
        durchlaufen = True
        while durchlaufen:
            zusatz_nr = random.randint(1, 12)
            if zusatz_nr in zusatz_liste:
                # Zusatz Zahl ist brereits vorhanden
                durchlaufen = True
            else:
                # Zusatz Zahl ist noch nicht vorhanden
                zusatz_liste.append(zusatz_nr)
                durchlaufen = False
    # Zusatz Zahlen sortieren
    zusatz_liste.sort()
    # Rückgabe
    return(zahlen_liste, zusatz_liste)


def set_random_draws():
    ''' Erstellt 1000 Zufallsziehungen '''
    # Dictionairy vorbereiten
    draw_dic = {'Datum': []}
    for zahl in DRAW_TOTAL:
        draw_dic[zahl] = []
    # Anzahl Ziehungen durchlaufen
    for draw_counter in range(1000):
        # Zeitstempel generieren
        date_now = datetime.datetime.now()
        date_now_text = date_now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        # Zufalls-Ziehung machen
        zahlen_liste, zusatz_liste = set_draw()
        # Zeitstempel dem Dicitionairy hinzufügen
        draw_dic['Datum'].append(date_now_text)
        # Zahlen dem Dictionairy hinzufügen
        draw_id = 0
        for zahl in DRAW_ZAHLEN:
            draw_dic[zahl].append(zahlen_liste[draw_id])
            # Index hochzählen
            draw_id += 1
        # Zusatz Zahlen dem Dictionairy hinzufügen
        draw_id = 0
        for zusatz in DRAW_ZUSATZ:
            draw_dic[zusatz].append(zusatz_liste[draw_id])
            # Index hochzählen
            draw_id += 1
        # Ausgabe und eine Hundertstel Sekunden warten
        print(f"Ziehung {draw_counter} = {zahlen_liste} {zusatz_liste}")
        time.sleep(0.01)
    # DataFrame erstellen
    df_draw = pd.DataFrame(draw_dic)
    # Bildschirm Ausgabe und Kontrolle
    print("\n[set_random_draws] df_draw")
    print(df_draw)
    print("[set_random_draws] gespeichert als random_draws.csv")
    df_draw.to_csv('random_draws.csv', index=False)
    # Rückgabe
    return(df_draw)


def set_sma_datas(df_extend):
    ''' Gleitende Durchschnitte mit dem SMA setzen '''
    # Vergangene Ziehungszahlen nach Index durchlaufen
    for zahl_id in range(len(DRAW_TOTAL)):
        # Keys auslesen
        draw_key = DRAW_TOTAL[zahl_id]
        avg_key = AVG_TOTAL[zahl_id]
        # SMA erstellen
        df_extend[avg_key] = df_extend[draw_key].\
            rolling(window=SMA_SIZE).mean()
        # SMA Werte skalieren
        df_extend[avg_key] *= SMA_SIZE
        # Terminal Output, Kontrolle
        print(f"\n[set_sma_datas] [{draw_key}]")
        print(df_extend[avg_key])
    # Terminal Output, Kontrolle
    print("\n[set_sma_datas] df_extend")
    print(df_extend)
    print("[set_sma_datas] gespeichert als sma_datas.csv")
    df_extend.to_csv('sma_datas.csv', index=False)
    # Rückgabe
    return(df_extend)


def set_target_dates(df_extend):
    ''' Ziel Datums-Daten setzen '''
    # Ziehungsdaten auslesen
    draw_date_list = df_extend['Datum'].tolist()
    # Liste für Zieldaten
    target_date_list = ['-'] * len(draw_date_list)
    # Ziehungsdaten nach Index durchlaufen
    for draw_id in range(len(draw_date_list)):
        if draw_id < len(draw_date_list) - 1:
            # Nächstes Datum existiert, Zieldatum setzen
            target_date_list[draw_id] = draw_date_list[draw_id + 1]
    # DataFrame ergänzen
    df_extend['Trg.Datum'] = target_date_list
    # Terminal Output, Kontrolle
    print("\n[set_target_dates] df_extend")
    print(df_extend)
    print("[set_target_dates] gespeichert als target_dates.csv")
    df_extend.to_csv('target_dates.csv', index=False)
    # Rückgabe
    return(df_extend)


def set_target_numbers(df_extend):
    ''' Ziel-Zahlen hinzufügen '''
    # Vergangene Ziehungszahlen nach Index durchlaufen
    for zahl_id in range(len(DRAW_TOTAL)):
        # Keys auslesen
        draw_key = DRAW_TOTAL[zahl_id]
        target_key = TARGET_TOTAL[zahl_id]
        # Ziehungszahlen als Liste
        draw_liste = df_extend[draw_key].tolist()
        # Liste für Zielzahlen
        target_liste = [0] * len(draw_liste)
        # Ziehungsdaten nach Index durchlaufen
        for ziel_id in range(len(draw_liste)):
            if ziel_id < len(draw_liste) - 1:
                # Nächste Ziehung existiert, Zielzahl setzen
                target_liste[ziel_id] = draw_liste[ziel_id + 1]
        # Ziehungsdataframe ergänzen
        df_extend[target_key] = target_liste
    # Terminal Output, Kontrolle
    print("\n[set_target_numbers] df_extend")
    print(df_extend)
    print("[set_target_numbers] gespeichert als target_numbers.csv")
    df_extend.to_csv('target_numbers.csv', index=False)
    # Rückgabe
    return(df_extend)


def set_log_regression(df_extend):
    ''' Für alle Zahlen eine logistische Regression machen '''
    # Zeitstempel & Dictionairy für Ziehungszahlen
    date_now = datetime.datetime.now()
    date_now_text = date_now.strftime("%Y-%m-%dT%H:%M:%S.%f")
    pred_draw_dic = {'Datum': date_now_text}
    for zahl_key in DRAW_TOTAL:
        pred_draw_dic[zahl_key] = None
    # Alle Ziel-Zahlen durchlaufen nach Index
    for zahl_id in range(len(TARGET_TOTAL)):
        # Ziel-Key & Ziehungs-Key auslesen
        target_key = TARGET_TOTAL[zahl_id]
        draw_key = DRAW_TOTAL[zahl_id]
        # Liste zum Daten auslesen
        draw_col_list = [target_key, draw_key]
        draw_col_list.extend(AVG_TOTAL)
        # Alle Spalten der Liste auslesen
        df_regr = df_extend[draw_col_list]
        # Leere SMA Werte abtrennen
        df_regr = df_regr[SMA_SIZE - 1:]
        # Alle Zahlen zu Integer
        df_regr = df_regr.astype(int)
        # Terminal Output, Kontrolle
        print("\n[set_log_regression] df_regr")
        print(df_regr)
        # Daten vorbereiten für logistische Regression
        df_x, df_y = log_reg_prepare_datas(
            df_regr,
            draw_key,
            target_key
        )


def log_reg_prepare_datas(df_regr, draw_key, target_key):
    ''' Trennt die Daten für logistische Regression in X und Y auf '''
    # X-Liste und Y-Text
    x_liste = [draw_key]
    x_liste.extend(AVG_TOTAL)
    y_text = target_key
    # Letzte Zeile als eigenes Dataframe abtrennen
    df_y = df_regr.tail(1)
    # Grundlagen Daten
    df_x = df_regr.copy()
    df_x.drop(df_y.index, inplace=True)
    # Terminal Output, Kontrolle
    t = "[log_reg_prepare_datas]"
    print(f"\n{t}x_liste")
    print(x_liste)
    print(f"{t}y_text")
    print(y_text)
    print(f"{t}df_x")
    print(df_x)
    print(f"{t}gespeichert als x_{target_key}.csv")
    df_x.to_csv(f'x_{target_key}.csv', index=False)
    print(f"{t}df_y")
    print(df_y)
    print(f"{t}gespeichert als y_{target_key}.csv")
    df_y.to_csv(f'y_{target_key}.csv', index=False)
    # Rückgabe
    return(df_x, df_y, x_liste, y_text)


def log_reg_proof(df_x, x_liste, y_text):
    ''' Logistische Regression trainieren und prüfen '''
    # Aufteilen in Trainings und Testdaten: 80/20%
    df_x_train, df_x_test, df_y_train, df_y_test = \
        train_test_split(
            df_x[x_liste],
            df_x[y_text],
            test_size=0.2,
            random_state=42
        )
    # Logistische Regression und Modell Training
    obRegr = LogisticRegression()
    obRegr.fit(df_x_train, df_y_train)
    # Genauigkeit und Koeffizient
    proof_score = obRegr.predict(df_x_test)
    text_score = str(accuracy_score(df_y_test, proof_score))
    # Score Wert als Float
    float_score = float(text_score)
    # Terminal Output, Kontrolle
    print("[log_reg_proof] float_score")
    print(float_score)


def log_reg_pred(df_daten, x_liste, y_text, df_y):
    ''' Voraussage mit Logistischer Regression machen '''
    # Logistische Regression und Modell Training
    obRegr = LogisticRegression()
    obRegr.fit(df_daten[x_liste], df_daten[y_text])
    # Voraussage
    df_pred_x = df_y[x_liste]
    pred = obRegr.predict(df_pred_x)
    # Voraussage als Float
    pred_float = float(pred)
    # Terminal Output, Kontrolle
    print("[LogReg.log_reg_pred] pred_float")
    print(pred_float)
    # Rückgabe
    return(pred_float)


def set_lotto_pred(df_extend):
    ''' Voraussage für nächste Lotto-Ziehung '''
    # Funktions-Code für Bildschirm Ausgabe
    t = "[set_lotto_pred] "
    # Zeitstempel generieren
    date_now = datetime.datetime.now()
    date_now_text = date_now.strftime("%Y-%m-%dT%H:%M:%S.%f")
    # Dictionairy vorbereiten
    pred_dic = {'Datum': date_now_text}
    for zahl in PROGNOSE_TOTAL:
        pred_dic[zahl] = []
    # Alle Ziel-Zahlen durchlaufen nach Index
    for zahl_id in range(len(PROGNOSE_TOTAL)):
        # Ziel-Key & Ziehungs-Key auslesen
        target_key = TARGET_TOTAL[zahl_id]
        draw_key = DRAW_TOTAL[zahl_id]
        pred_key = PROGNOSE_TOTAL[zahl_id]
        # Bildschirm Ausgabe
        print(f"\n{t}target_key: {target_key}")
        print(f"{t}draw_key: {draw_key}")
        print(f"{t}pred_key: {pred_key}")
        # Liste zum Daten auslesen
        key_list = [target_key, draw_key]
        key_list.extend(AVG_TOTAL)
        # Daten auslesen
        df_daten = df_extend[key_list]
        # Leere SMA Werte abtrennen
        df_daten = df_daten[SMA_SIZE - 1:]
        # Zahlen zu Integer wandeln
        df_daten = df_daten.astype(int)
        # Bildschirm Ausgabe, Kontrolle
        print(f"{t}<{pred_key}> df_daten")
        print(df_daten)
        print(f"{t}gespeichert als datas_{pred_key}.csv")
        df_daten.to_csv(f'datas_{pred_key}.csv', index=False)
        # Daten für logistische Regression vorbereiten
        df_x, df_y, x_liste, y_text = log_reg_prepare_datas(
            df_daten,
            draw_key,
            target_key
        )
        # Logistische Regression prüfen
        float_score = log_reg_proof(df_x, x_liste, y_text)
        # Logistische Regression machen
        pred_float = log_reg_pred(df_daten, x_liste, y_text, df_y)
        # Prognose in Ziehung-Dictionairy eintragen
        pred_dic[pred_key] = int(pred_float)
    # Bildschirm Ausgabe, Kontrolle
    print(f"{t}Prognose pred_dic")
    print(pred_dic)
    # Rückgabe
    return(pred_dic)


def set_random_draw():
    ''' Erstellt eine Zufalls-Ziehung '''
    # Funktions-Code für Bildschirm Ausgabe
    t = "[set_random_draw] "
    # Zeitstempel generieren
    date_now = datetime.datetime.now()
    date_now_text = date_now.strftime("%Y-%m-%dT%H:%M:%S.%f")
    # Dictionairy vorbereiten
    draw_dic = {'Datum': date_now_text}
    for zahl in DRAW_TOTAL:
        draw_dic[zahl] = []
    # Zufalls-Ziehung machen
    zahlen_liste, zusatz_liste = set_draw()
    # Zeitstempel dem Dicitionairy hinzufügen
    draw_dic['Datum'] = date_now_text
    # Zahlen dem Dictionairy hinzufügen
    draw_id = 0
    for zahl in DRAW_ZAHLEN:
        draw_dic[zahl] = zahlen_liste[draw_id]
        # Index hochzählen
        draw_id += 1
    # Zusatz Zahlen dem Dictionairy hinzufügen
    draw_id = 0
    for zusatz in DRAW_ZUSATZ:
        draw_dic[zusatz] = zusatz_liste[draw_id]
        # Index hochzählen
        draw_id += 1
    # Bildschirm Ausgabe und Kontrolle
    print(f"\n{t}draw_dic")
    print(draw_dic)
    # Rückgabe
    return(draw_dic)


def set_evaluation(pred_dic, ref_dic, draw_dic):
    ''' Vergleich der Ziehungen '''
    # Funktions-Code für Bildschirm Ausgabe
    t = "[set_evaluation] "
    # Anzahl Richtige für Prognose und Zufalls-Referenz
    correct_pred_zahl = 0
    correct_pred_zusatz = 0
    correct_ref_zahl = 0
    correct_ref_zusatz = 0
    # Lotto-Ziehung mit Voraussage Zahlen vergleichen
    for zahl in DRAW_ZAHLEN:
        # Jede Zahl aus der Ziehung vergleichen
        for prognose in PROGNOSE_ZAHLEN:
            if draw_dic[zahl] == pred_dic[prognose]:
                # Richtige Voraussage Zahl
                correct_pred_zahl += 1
    # Lotto-Ziehung mit Voraussage Zusatz vergleichen
    for zusatz in DRAW_ZUSATZ:
        # Jeder Zusatz aus der Ziehung vergleichen
        for prognose in PROGNOSE_ZUSATZ:
            if draw_dic[zusatz] == pred_dic[prognose]:
                # Richtiger Voraussage Zusatz
                correct_pred_zusatz += 1
    # Lotto-Ziehung mit Referenz Zahlen vergleichen
    for zahl in DRAW_ZAHLEN:
        # Jede Zahl aus der Ziehung vergleichen
        for ref in DRAW_ZAHLEN:
            if draw_dic[zahl] == ref_dic[ref]:
                # Richtige Referenz Zahl
                correct_ref_zahl += 1
    # Lotto-Ziehung mit Referenz Zusatz vergleichen
    for zusatz in DRAW_ZUSATZ:
        # Jeder Zusatz aus der Ziehung vergleichen
        for ref in DRAW_ZUSATZ:
            if draw_dic[zusatz] == ref_dic[ref]:
                # Richtiger Referenz Zusatz
                correct_ref_zusatz += 1
    # Bildschirm Ausgabe und Kontrolle
    t2 = f"\n{t}Richtige Zahlen Prognose, correct_pred_zahl: "
    print(f"{t2}{correct_pred_zahl}")
    t2 = f"{t}Richtige Zusatz-Zahlen Prognose, correct_pred_zusatz: "
    print(f"{t2}{correct_pred_zusatz}")
    t2 = f"{t}Richtige Zahlen Referenz, correct_ref_zahl: "
    print(f"{t2}{correct_ref_zahl}")
    t2 = f"{t}Richtige Zusatz-Zahlen Referenz, correct_ref_zusatz: "
    print(f"{t2}{correct_ref_zusatz}")
    # Rückgabe
    richtige = [
        correct_pred_zahl,
        correct_pred_zusatz,
        correct_ref_zahl,
        correct_ref_zusatz
    ]
    return(richtige)


def add_draw(df_basic_draws, draw_dic):
    ''' Hängt die Ziehung an die Grundlagen '''
    # Funktions-Code für Bildschirm Ausgabe
    t = "[add_draw] "
    # Zu Ziehungs-Dictionairy mit Listen-Werten wändeln
    draw_dic_new = {}
    for key, value in draw_dic.items():
        draw_dic_new[key] = [value]
    print(f"{t} draw_dic_new")
    print(draw_dic_new)
    # Pandas erstellen
    df_draw = pd.DataFrame(draw_dic_new)
    print(f"{t}df_draw")
    print(df_draw)
    print(f"{t}gespeichert als draw.csv")
    df_draw.to_csv('draw.csv', index=False)
    # Grundlagen Ziehung erweitern
    df_basic_draws = pd.concat(
        [df_basic_draws, df_draw],
        ignore_index=True
    )
    print(f"{t}df_basic_draws")
    print(df_basic_draws)
    print(f"{t}gespeichert als basic_draws.csv")
    df_basic_draws.to_csv('basic_draws.csv', index=False)
    # Rückgabe
    return(df_basic_draws)


if __name__ == '__main__':
    ''' Zufalls-Lotto Spiel '''
    # Funktions-Code für Bildschirm Ausgabe
    t = "[main] "
    # Paramter Kontrolle
    t2 = "PARAMETER KONTROLLE"
    u = (len(t) + len(t2)) * '-'
    print(f"\n\n{u}\n{t}{t2}\n{u}")
    print(f"{t}DRAW_ZAHLEN: {DRAW_ZAHLEN}")
    print(f"{t}DRAW_ZUSATZ: {DRAW_ZUSATZ}")
    print(f"{t}DRAW_TOTAL: {DRAW_TOTAL}")
    print(f"{t}PROGNOSE_ZAHLEN: {PROGNOSE_ZAHLEN}")
    print(f"{t}PROGNOSE_ZUSATZ: {PROGNOSE_ZUSATZ}")
    print(f"{t}PROGNOSE_TOTAL: {PROGNOSE_TOTAL}")
    print(f"{t}AVG_ZAHLEN: {AVG_ZAHLEN}")
    print(f"{t}AVG_ZUSATZ: {AVG_ZUSATZ}")
    print(f"{t}AVG_TOTAL: {AVG_TOTAL}")
    print(f"{t}TARGET_ZAHLEN: {TARGET_ZAHLEN}")
    print(f"{t}TARGET_ZUSATZ: {TARGET_ZUSATZ}")
    print(f"{t}TARGET_TOTAL: {TARGET_TOTAL}")
    # Titel
    t2 = "ZLM24  ZUFALLS-LOTTO MACHINE-LEARNING"
    u = (len(t) + len(t2)) * '-'
    print(f"\n\n{u}\n{t}{t2}\n{u}")
    # Zufalls Grundlagen erstellen
    print(f"{t}1000 Zufalls-Grundlagen erstellen")
    eingabe = input("[ENTER] für weiter")
    df_basic_draws = set_random_draws()
    # Modus wählen
    t2 = "MODUS FÜR ZUFALLS-LOTTO WÄHLEN"
    u = (len(t) + len(t2)) * '-'
    print(f"\n\n{u}\n{t}{t2}\n{u}")
    print(f"{t}1 = Demonstration Schritt für Schritt")
    print(f"{t}2 = Vergleich mit der Eingabe Anzahl Durchläufe")
    modus = input("Ihre Wahl, 1 oder 2 .. ")
    if modus == "2":
        # Anzahl Durchläufe abfragen
        print(f"\n{t}Anzahl der Durchläufe eingaben")
        iterationen = int(input("Ihre Eingabe, 1 - .. "))
    else:
        iterationen = 1
    # Bildschirm Ausgabe
    print(f"\n{t}modus: {modus}")
    print(f"{t}iterationen: {iterationen}")
    # Dictionairy für Vergleich
    eval_dic = {
        'PRED-ZAHL': [],
        'PRED-ZUSATZ': [],
        'REF-ZAHL': [],
        'REF-ZUSATZ': []
    }
    # Iterationen
    for iter_id in range(iterationen):
        # Grundlagen erweitern
        df_extend = df_basic_draws.copy()
        # SMA hinzufügen
        t2 = "GRUNDLAGEN MIT GLEITENDEN DURSCHSCHNITTEN ERWEITERN"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        df_extend = set_sma_datas(df_extend)
        # Ziel Daten hinzufügen
        t2 = "GRUNDLAGEN MIT ZIEL DATUMS-DATEN ERWEITERN"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        df_extend = set_target_dates(df_extend)
        # Ziel Zahlen hinzufügen
        t2 = "GRUNDLAGEN MIT ZIEL ZAHLEN ERWEITERN"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        df_extend = set_target_numbers(df_extend)
        # Prognose mit Logistischer Regression
        t2 = "VORAUSSAGE NÄCHSTER LOTTO ZAHLEN"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        pred_dic = set_lotto_pred(df_extend)
        # Zufalls-Tipp als Vergleich zu Prognose
        t2 = "ZUFALLS-TIPP ALS REFERENZ ZUR PROGNOSE"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        ref_dic = set_random_draw()
        # Zufalls-Lotto Ziehung
        t2 = "ZUFALLS-LOTTO-ZIEHUNG"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        draw_dic = set_random_draw()
        # Ziehungen vergleichen
        t2 = "ZIEHUNGEN VERGLEICHEN"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        richtige = set_evaluation(pred_dic, ref_dic, draw_dic)
        # Ans Vergleich Dictionairy hinzufügen
        eval_dic['PRED-ZAHL'].append(richtige[0])
        eval_dic['PRED-ZUSATZ'].append(richtige[1])
        eval_dic['REF-ZAHL'].append(richtige[2])
        eval_dic['REF-ZUSATZ'].append(richtige[3])
        # Basis mit Zufalls-Ziehung erweitern
        t2 = "GRUNDLAGEN MIT ZUFALLS-ZIEHUNG ERWEITERN"
        u = (len(t) + len(t2)) * '-'
        print(f"\n\n{u}\n{t}{t2}\n{u}")
        if modus == "1":
            eingabe = input("[ENTER] für weiter")
        df_basic_draws = add_draw(df_basic_draws, draw_dic)
    # Abschluss, Summe der richtigen Zahlen
    sum_pred_zahl = sum(eval_dic['PRED-ZAHL'])
    sum_pred_zusatz = sum(eval_dic['PRED-ZUSATZ'])
    sum_ref_zahl = sum(eval_dic['REF-ZAHL'])
    sum_ref_zusatz = sum(eval_dic['REF-ZUSATZ'])
    # Richtige nach Anzahl Zahlen
    pred_richtige_dic = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0
    }
    ref_richtige_dic = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0
    }
    # Vergleichs-Dictionairy durchlaufen
    for eval_id in range(iterationen):
        # Richtige Prognose und Referenz
        sum_pred_richtig = eval_dic['PRED-ZAHL'][eval_id] + \
            eval_dic['PRED-ZUSATZ'][eval_id]
        sum_ref_richtig = eval_dic['REF-ZAHL'][eval_id] + \
            eval_dic['REF-ZUSATZ'][eval_id]
        # Anhand der Anzahl Richtigen ins Dictionairy eintragen
        pred_richtige_dic[sum_pred_richtig] += 1
        ref_richtige_dic[sum_ref_richtig] += 1
    # Ausgabe
    t2 = "DIE ERGEBNISSE"
    u = (len(t) + len(t2)) * '-'
    print(f"\n\n{u}\n{t}{t2}\n{u}")
    print(f"{t}Anzahl Durchläufe: {iterationen}")
    print(f"{t}Richtige Zahlen aus Prognose: {sum_pred_zahl}")
    print(f"{t}Richtige Zusatz-Zahlen aus Prognose: {sum_pred_zusatz}")
    print(f"{t}Richtige Zahlen aus Referenz: {sum_ref_zahl}")
    print(f"{t}Richtige Zusatz-Zahlen aus Referenz: {sum_ref_zusatz}")
    print(f"\n{t}Anzahl 0 Richtige Progonse: {pred_richtige_dic[0]}")
    print(f"{t}Anzahl 1 Richtige Progonse: {pred_richtige_dic[1]}")
    print(f"{t}Anzahl 2 Richtige Progonse: {pred_richtige_dic[2]}")
    print(f"{t}Anzahl 3 Richtige aus Progonse: {pred_richtige_dic[3]}")
    print(f"{t}Anzahl 4 Richtige aus Progonse: {pred_richtige_dic[4]}")
    print(f"{t}Anzahl 5 Richtige aus Progonse: {pred_richtige_dic[5]}")
    print(f"{t}Anzahl 6 Richtige aus Progonse: {pred_richtige_dic[6]}")
    print(f"{t}Anzahl 7  Richtige aus Progonse: {pred_richtige_dic[7]}")
    print(f"\n{t}Anzahl 0 Richtige aus Referenz: {ref_richtige_dic[0]}")
    print(f"{t}Anzahl 1 Richtige aus Referenz: {ref_richtige_dic[1]}")
    print(f"{t}Anzahl 2 Richtige aus Referenz: {ref_richtige_dic[2]}")
    print(f"{t}Anzahl 3 Richtige aus Referenz: {ref_richtige_dic[3]}")
    print(f"{t}Anzahl 4 Richtige aus Referenz: {ref_richtige_dic[4]}")
    print(f"{t}Anzahl 5 Richtige aus Referenz: {ref_richtige_dic[5]}")
    print(f"{t}Anzahl 6 Richtige aus Referenz: {ref_richtige_dic[6]}")
    print(f"{t}Anzahl 7  Richtige aus Referenz: {ref_richtige_dic[7]}")
    t2 = "Vielen Dank für Ihr Interesse .. [ENTER] für weiter"
    eingabe = input(f"\n{t2}")
