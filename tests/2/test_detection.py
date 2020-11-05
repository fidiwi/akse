"""
Title:       Überprüfen der korrekten Erkennung von Kontrollstrukturen

Description: Es soll getestet werden, ob die Kontrollstrukturerkennung von
             AKsE.py wie erwartet funktioniert. Hierfür soll in diesem Fall das Programm
             die geforderten Kontrollstrukturen "if", "else if" und "else" 
             der Datei input.cpp nicht mit /*X*/ markieren, da die Kontrollstrukturen 
             auskommentiert sind. Die bearbeitete Datei gibt es als 
             output.cpp aus. Die input.cpp und config.json Dateien werden für
             den Testfall manuell erstellt. Eine erwartete Ausgabe wird ebenfalls
             erstellt als die Datei output_expected.cpp. Zur Überprüfung werden dann die Ausgabe des 
             Programms (output.cpp) und die erwartete Ausgabe (output_expected)
             verglichen.

Requirement: 
    #2.2.1.4

Preconditions:
    1) config.json, input.cpp, output_expected.cpp, AKsE.py und diese Datei müssen sich
        im selben Ordner befinden.

Test method: Functional/Black-Box Test

Action: 
    1) (Automatisches) generieren der Dateien "config.json", "input.cpp" und "output_expected.cpp".
        Dabei beinhaltet "input.cpp" die Kontrollstrukturen "if", "else if" und "else", allerdings in auskommentierter Form. 
        In der config.json muss Punkt 1 unter "detect" angefordert sein.
    2) Starten des Programms AKsE.py

Reaction:
    1) Ausgabe der Datei "output.cpp" durch "AKsE.py". Diese Datei enthält keine Markierung an den jeweilig
       angeforderten Kontrollstrukturen "if", "else if" und "else", da sie auskommentiert sind.
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
