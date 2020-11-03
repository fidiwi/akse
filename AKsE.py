from operator import itemgetter
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
pattern_else = r"(?<=if\s*\((.*?)\)\s*\{([\s\S]*?)\}(\s*?))else\s*\{"
pattern_elif = r"(?<=if\s*\((.*?)\)\s*\{([\s\S]*?)\}(\s*?))else if\s*\{"

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
print(pattern_case)
patterns = {
    1: {"a": pattern_if,
        "b": pattern_else,
        "c": pattern_elif},
    2: {"a": pattern_for,
        "b": pattern_while,
        "c": pattern_do_while},
    3: {"a": pattern_switch,
        "b": pattern_case,
        "c": pattern_default}}


class Config:
    def readConfig(self):
        with open(config_path) as json_file:
            try:
                data = json.load(json_file)
                self.detect = data["detect"]               
            except Exception:
                # 2.2.2.5_Konfigurationsdatei#REAL
                sys.exit("[Error] Could not load JSON File")


class Analysis:

    def __init__(self, detect):
        self.detect = detect

    def readCPP(self):
        with open(cpp_path, "r") as cpp_file:
            self.cpp_content = cpp_file.read()
        
    def detectCommentedCode(self):
        
        # For /* XYZ */ structures
        pattern1 = regex.compile(r"\/\*(.*?)\*\/", regex.DOTALL)
        result1 = regex.finditer(pattern1, self.cpp_content)

        # For //XYZ structures
        pattern2 = regex.compile(r"\/\/(.*?)\n", regex.DOTALL)
        result2 = regex.finditer(pattern2, self.cpp_content)

        self.list_commented = []
        for match in result1:
            self.list_commented.append(match.span())

        for match in result2:
            self.list_commented.append(match.span())

        # print(list_commented)
    
    def detectControlStructures(self):
        results = []
        for group in self.detect:
            if group == 1:
                for i in ("a", "b", "c"):
                    pattern = regex.compile(patterns[1][i], regex.DOTALL)
                    result = regex.finditer(pattern, self.cpp_content)
                    results.append(result)
            elif group == 2:
                for i in ("a", "b", "c"):
                    pattern = regex.compile(patterns[2][i], regex.DOTALL)
                    result = regex.finditer(pattern, self.cpp_content)
                    results.append(result)
            elif group == 3:
                for i in ("a", "b", "c"):
                    pattern = regex.compile(patterns[3][i], regex.DOTALL)
                    result = regex.finditer(pattern, self.cpp_content)
                    results.append(result)
            else:
                sys.exit(str("[Error] Group '" + str(group) + "' requested in \
                    config.json does not exist."))
        
        return results

    def validateDetection(self, detected_data):
        content_edited = self.cpp_content
        result_list = []

        for iterator in detected_data:
            for item in iterator:
                result_list.append(item.span())

        # 2.2.4.1_Fehler#REAL
        if(len(result_list) == 0):
            sys.exit("[Error] None of the requested ",
                     "control structres were detected")
        # Sort list items by their ending position AND reverse it.
        reversed_list = sorted(result_list, key=itemgetter(1), reverse=True)
        for match in reversed_list:
            start = match[0]
            insideComments = False
            
            # Check if Statement is within comments
            for comments in self.list_commented:
                if comments[0] <= start <= comments[1]:
                    insideComments = True
                    break
            
            if (not insideComments):
                end = match[1]
                content_edited = content_edited[:end] + "/*X*/" \
                    + content_edited[end:]
        print(content_edited)
        return content_edited


config = Config()
config.readConfig()

detect = config.detect

# If length of "detect" is 0
# 2.2.4.2_Fehler#REAL
if not len(detect):
    sys.exit("[Info] Program closed - No control structure requested ",
             "in JSON File")

analysis = Analysis(detect)
analysis.readCPP()
analysis.detectCommentedCode()
results = analysis.detectControlStructures()
cpp_commented = analysis.validateDetection(results)
with open("output.cpp", "w") as file:
    file.truncate()
    file.write(cpp_commented)   