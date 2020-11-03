import json
import sys
import regex

# re Multiline comments
# \/\*(.*?)\*\/
# \/\*([\S\s]*?)\*\/

# re Singleline comments
# \/\/(.*?)\n
config_path = "config.json"
cpp_path = "input.cpp"

pattern_if = r"if(\s*?)\((.*?)\)(\s*?)\{"
pattern_else = r"(?<=if\s*\((.*?)\)\s*\{([\s\S]*?)\}(\s*?))else([\s\S]*?)\{"
pattern_elif = r"(?<=if\s*\((.*?)\)\s*\{([\s\S]*?)\}(\s*?))else\s*if(\s*?)"\
    r"\((.*?)\)(\s*?)\{"

# CHANGE: "Do-Schleife" aus REQs entfernen
pattern_for = r"for(\s*?)\((.*?)\)(\s*?)\{"
pattern_while = r"while(\s*?)\((.*?)\)(\s*?)\{"
pattern_do_while = r"do\s*\{(?=([\s\S]*?)\}\s*while\s*\(([\s\S]*?)\);)"


pattern_switch = r"switch(\s*?)\((.*?)\)(\s*?)\{"
pattern_switch_case_default = r"switch(\s*?)\((.*?)\)(\s*?)\{\s*(case\s*(.*?)"\
    r":(.*?);)+\s*default:(.*?);\s*\}"
pattern_case = r"case\s*(.*?):((?=(.*?);\s*default:(.*?);+\s*\})|(?=(.*?);\s*"\
    "case(.*?):(.*?);))"
pattern_default = r"default:(?=(.*?);+\s*\})"
patterns = [
    [pattern_if,
     pattern_else,
     pattern_elif],
    [pattern_for,
     pattern_while,
     pattern_do_while],
    [pattern_switch,
     pattern_case,
     pattern_default]]


# Config class for reading in the config.json file and checking its format
class Config:
    def readConfig(self, path):
        with open(path) as json_file:
            try:
                data = json.load(json_file)
                self.detect = data["detect"]               
            except Exception as e:
                # 2.2.2.5_Konfigurationsdatei#REAL
                sys.exit("[Error] Could not load JSON File: " + str(e))


# Analysis class for reading the input.cpp file. Also to detect
# requested control structures and to mark them
class Analysis:

    def __init__(self, detect):
        self.detect = detect

    def readCPP(self, path):
        # 2.2.5.1_Eingabe#REAL
        with open(path, "r") as cpp_file:
            cpp_content = cpp_file.read()
            return cpp_content
        
    def detectCommentedCode(self, cpp_content):
        
        # For /* XYZ */ structures
        patternMultilineComment = regex.compile(r"\/\*(.*?)\*\/", regex.DOTALL)
        resultMultilineComment = regex.finditer(patternMultilineComment,
                                                cpp_content)

        # For //XYZ structures
        patternSinglelineComment = regex.compile(r"\/\/(.*?)\n", regex.DOTALL)
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
                pass
                for i in range(len(patterns[group-1])):
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
            sys.exit("[Error] None of the requested ",
                     "control structures were detected")
        # Sort list items by their ending position AND reverse it.
        reversed_list = sorted(result_list, key=lambda x: x[1], reverse=True)
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


config = Config()
config.readConfig(config_path)

detect = config.detect

# If length of "detect" is 0
# 2.2.4.2_Fehler#REAL
if not len(detect):
    sys.exit("[Info] Program closed - No control structure requested ",
             "in JSON File")

analysis = Analysis(detect)
content = analysis.readCPP(cpp_path)
list_commented = analysis.detectCommentedCode(content)
results = analysis.detectControlStructures(content)
cpp_commented = analysis.validateDetection(content, list_commented, results)

with open("output.cpp", "w") as file:
    file.truncate()
    file.write(cpp_commented)   