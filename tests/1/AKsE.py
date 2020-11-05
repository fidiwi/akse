import json
import sys
import regex # REVIEW(BEM): Möglichst "re" aus Standard-Bibliothek benutzen
             # AW(FRW): Beim testen hat "re" ungewiss lange patterns mit lookaround (z.B. "(?<=\s*)") nicht unterstützt.

# re Multiline comments
# \/\*(.*?)\*\/
# \/\*([\S\s]*?)\*\/

# re Singleline comments
# \/\/(.*?)\n
config_path = "config.json"
cpp_path = "input.cpp"

pattern_if = r"if(\s*?)\((.*?)\)(\s*?)\{" # REVIEW(BEM): Funktioniert das auch bei so einer Zeile: if(a && (b || (c && d))) - also geschachtelte Klammern?
                                          # AW(FRW): Ja.
pattern_else = r"(?<=if\s*\((.*?)\)\s*\{([\s\S]*?)\}(\s*?))else([\s\S]*?)\{" # REVIEW(BEM): Wenn ein Kommentar zwischen else und { funktioniert das nicht
                                                                             # AW(FRW): Pattern verändert.
pattern_elif = r"(?<=if\s*\((.*?)\)\s*\{([\s\S]*?)\}(\s*?))else\s*if(\s*?)"\
    r"\((.*?)\)(\s*?)\{"  # REVIEW(BEM): Bei Zeilenumbruch zwischen else und if funktioniert das nicht
                          # AW(FRW): Pattern verändert.

# CHANGE: "Do-Schleife" aus REQs entfernen
pattern_for = r"for(\s*?)\((.*?)\)(\s*?)\{"
pattern_while = r"while(\s*?)\((.*?)\)(\s*?)\{"
pattern_do_while = r"do\s*\{(?=([\s\S]*?)\}\s*while\s*\(([\s\S]*?)\);)"

# REVIEW(BEM): unnötige Debug-Ausgaben bitte entfernen
# AW(FRW): Geändert.

pattern_switch = r"switch(\s*?)\((.*?)\)(\s*?)\{"
pattern_switch_case_default = r"switch(\s*?)\((.*?)\)(\s*?)\{\s*(case\s*(.*?)"\
    r":(.*?);)+\s*default:(.*?);\s*\}"
pattern_case = r"case\s*(.*?):((?=(.*?);\s*default:(.*?);+\s*\})|(?=(.*?);\s*"\
    "case(.*?):(.*?);))"
pattern_default = r"default:(?=(.*?);+\s*\})"
patterns = [  # REVIEW(BEM): Diese Struktur ist ungünstig: warum 1,2,3? Warum a,b,c?
              # AW(FRW): Struktur geändert.
    [pattern_if,
     pattern_else,
     pattern_elif],
    [pattern_for,
     pattern_while,
     pattern_do_while],
    [pattern_switch,
     pattern_case,
     pattern_default]]

# REVIEW(BEM): In dieser Klasse fehlt die Kommentierung (Wofür ist die Klasse da?)
# AW(FRW): Beschreibung hinzugefügt.

# Config class for reading in the config.json file and checking its format
class Config:

    def __init__(self, path):
        self.path = path

    def readConfig(self):  # REVIEW(BEM): Besser den Pfad zur Config-Datei als Parameter übergeben
                                 # AW(FRW): Änderung angenommen.
        with open(self.path) as json_file:
            try:
                data = json.load(json_file)
                self.detect = data["detect"]               
            except Exception as e:  # REVIEW(BEM): Den Inhalt der Exception sollte man mit ausgeben, sonst weiß der Benutzer nicht was er falsch gemacht hat
                                    # AW(FRW): Änderung angenommen.
                # 2.2.2.5_Konfigurationsdatei#REAL
                sys.exit("[Error] Could not load JSON File: " + str(e))


# REVIEW(BEM): In dieser Klasse fehlt die Kommentierung (Wofür ist die Klasse da?)
# AW(FRW): Beschreibung hinzugefügt.

# Analysis class for reading the input.cpp file. Also to detect
# requested control structures and to mark them
class Analysis:

    def __init__(self, detect):
        self.detect = detect

    def readCPP(self, path): # REVIEW(BEM): Besser den Pfad zur Cpp-Datei als Parameter übergeben
                             # AW(FRW): Änderung angenommen.
        # 2.2.5.1_Eingabe#REAL
        with open(path, "r") as cpp_file:
            cpp_content = cpp_file.read()
            return cpp_content
        
    def detectCommentedCode(self, cpp_content):
        
        # For /* XYZ */ structures
        patternMultilineComment = regex.compile(r"\/\*(.*?)\*\/", regex.DOTALL) # REVIEW(BEM): Die Variablennamen bitte aussagekräftiger wählen - unter "pattern1" kann man sich nicht viel vorstellen
                                                                                # AW(FRW): Variablennamen angepasst.
        resultMultilineComment = regex.finditer(patternMultilineComment,
                                                cpp_content) # REVIEW(BEM): wenn man vorher nicht die Methode "readCPP" aufgerufen hat ist self.cpp_content hier undefiniert
                                                             # AW(FRW): Problem behoben (siehe unten).

        # For //XYZ structures
        patternSinglelineComment = regex.compile(r"\/\/(.*?)\n", regex.DOTALL)  # REVIEW(BEM): Was passiert wenn sowas passiert: /*  // */ ? oder /* /* */ ?
                                                                # AW(FRW): Der zweite Fall wird wie erwartet erkannt, der erste leider noch nicht.
                                                                # Ich finde hierfür keine passendes Pattern, hast du eine Idee? Anonsten müsste man
                                                                # innerhalb der erkannten Kommentare nach dieser spezifischen Struktur suchen.
        resultSinglelineComment = regex.finditer(patternSinglelineComment,
                                                 cpp_content)

        list_commented = []
        for match in resultMultilineComment:
            list_commented.append(match.span())

        for match in resultSinglelineComment:
            list_commented.append(match.span())
        return list_commented

    def detectControlStructures(self, cpp_content):
        results = []
        # 2.2.1.1_Einschr#REAL
        for group in self.detect:
            if group-1 in range(0, 3): 
                for i in range(len(patterns[group-1])):  # REVIEW(BEM): siehe oben: 1/2/3 und a/b/c verstehe ich nicht. Außerdem enthält der Code in dieser Methode sehr viel Copy-Paste, also drei Mal das gleiche
                                                         # AW(FRW): Verändert.
                    pattern = regex.compile(patterns[group-1][i], regex.DOTALL)
                    result = regex.finditer(pattern, cpp_content)
                    results.append(result)
            else:
                # 2.2.2.4_Konfigurationsdatei#REAL
                sys.exit(str("[Error] Group '" + str(group) + "' requested in",
                             " config.json does not exist."))
        
        return results

    def validateDetection(self, cpp_content, list_commented, detected_data):
        content_edited = cpp_content
        result_list = []

        for iterator in detected_data:
            for item in iterator:
                result_list.append(item.span())

        # 2.2.4.1_Fehler#REAL
        # 2.2.5.2_Eingabe#REAL
        if(len(result_list) == 0):
            sys.exit("[Error] None of the requested " +
                     "control structures were detected")  # REVIEW(BEM): Tippfehler
                                                          # AW(FRW): Korrigiert.
        # Sort list items by their ending position AND reverse it.
        reversed_list = sorted(result_list, key=lambda x: x[1], reverse=True)  # REVIEW(BEM): Anstatt itemgetter kann man das auch mit einem Lambda machen, das ist lesbarer
                                                                               # AW(FRw): Änderung angenommen.
        print(reversed_list)
        for match in reversed_list:
            start = match[0]
            insideComments = False
            
            # Check if Statement is within comments
            # 2.2.1.4_Einschr#REAL
            for comments in list_commented:
                if comments[0] <= start <= comments[1]:
                    insideComments = True
                    break
            
            if (not insideComments):
                end = match[1]
                # 2.2.3_Markierung#REAL
                content_edited = content_edited[:end] + "/*X*/" \
                    + content_edited[end:]
        print(content_edited)
        return content_edited


def startProgram():

    config = Config(config_path)
    config.readConfig()

    detect = config.detect

    # If length of "detect" is 0
    # 2.2.4.2_Fehler#REAL
    if not len(detect):
        sys.exit("[Info] Program closed - No control structure requested ",
                 "in JSON File")

    analysis = Analysis(detect)
    content = analysis.readCPP(cpp_path) # REVIEW(BEM): Methoden ohne Parameter und ohne Rückgabewert machen eine Klasse meistens schwer benutzbar,
    # denn sie verändern interne Variablen, aber der Aufrufer bekommt nichts zurück. Das führt dazu, dass man wissen muss in welcher Reihenfolge 
    # man Methoden aufrufen muss (und eine falsche Reihenfolge führt wie oben angemerkt zu Fehlern). Das könnte man hier verbessern indem "readCpp"
    # cpp_content zurückgibt, und cpp_content dann als Paramter für detectCommentedCode dient, usw. (dadurch erzwingt man die richtige Reihenfolge)
    # AW(FRW): Abhängigkeiten zwischen den Methoden geschaffen.
    list_commented = analysis.detectCommentedCode(content)
    results = analysis.detectControlStructures(content)
    cpp_commented = analysis.validateDetection(content, list_commented, results)

    with open("output.cpp", "w") as file:
        file.truncate()
        file.write(cpp_commented)


if __name__ == "__main__":
    startProgram()
