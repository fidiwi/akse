"""
Title:       Überprüfen der korrekten Erkennung von Kontrollstrukturen

Description: Es soll getestet werden, ob die Kontrollstrukturerkennung von
             AKsE.py wie erwartet funktioniert. Hierfür markiert das Programm
             geforderte Kontrollstrukturen der Datei input.cpp mit /*X*/ und 
             gibt die bearbeitete Datei als output.cpp aus. Die input.cpp 
             und config.json Dateien werden für den Testfall manuell erstellt.
             Eine erwartete Ausgabe wird ebenfalls erstellt unter der Datei
             output_expected.cpp. Zur Überprüfung werden dann die Ausgabe des 
             Programms (output.cpp) und die erwartete Ausgabe (output_expected)
             verglichen.

Requirement: 
    #2.2.1
    #2.2.2
    #2.2.3
    #2.2.5

Preconditions:
    1) config.json, input.cpp, output_expected.cpp, AKsE.py und diese Datei müssen sich
        im selben Ordner befinden.

Test method: Functional/Black-Box Test

Action: 
    1) (Automatisches) generieren der Dateien "config.json", "input.cpp" und "output_expected.cpp"
    2) Starten des Programms AKsE.py

Reaction:
    1) Ausgabe der Datei "output.cpp" durch "AKsE.py"
    2) Vergleichen der Ausgabe ("output.cpp") mit der erwarteten Ausgabe ("output_expected.cpp")

"""
import pytest
import os
import AKsE
import filecmp


def test():
    AKsE.startProgram()
    file_output = "output.cpp"
    file_expected = "output_expected.cpp"

    comp = filecmp.cmp(file_expected, file_output, shallow=False)

    assert comp
