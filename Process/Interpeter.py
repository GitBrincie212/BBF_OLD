#!/usr/bin/env python
import ply, re, os, json, time
from time import sleep
from os import system as os_system
from ply import lex

Error = [0, None, None]
Output_Error_Color = "\033[31m[ERROR]\033[0m\033[1;31m"
Output_Warning_Color = "\033[33m[WARNING]\033[0m\033[1;33m"
Reset = "\033[0m"
triangle_increment_list = [[[], []]]
triangle_decrement_list = [[[], []]]
triangle_out_list = [[[], []]]
triangle_twice_list = [[[], []]]

def Repeater_Warn(line):
     print (f"{Output_Warning_Color} Repeater Has Nothing To Copy Paste Into, On Line {line + 1}{Reset}")
     return 0, True

def Error_Handler(line, line_value, Tokens):
    global t_ENDLINE
    ENDLINE = t_ENDLINE.replace ( "\\", "" )
    Warned = False
    def Warning(Color, String, Warned=Warned):
        Warned = True
        print (f"{Color} {String}{Reset}")
        return Warned
    Error = lambda Color, String: print ( f"{Color} {String}{Reset}" )
    true_line_value = line_value[line_value.find(ENDLINE):]
    if (find := true_line_value.find("#")) >= 1:
      true_line_value = true_line_value[:find]
    true_line_value = true_line_value.replace(" ", "")
    if len ( line_value ) == 0: return 0
    elif true_line_value[-1] != ENDLINE and not line_value.replace(" ", "").startswith("#"):
        Error(Output_Error_Color, f"Endline Character Was Not Called on Line {line + 1}")
        return -1
    elif ENDLINE in true_line_value[0:-1] :
        Error(Output_Error_Color, f"Endline Character Was Used More than Once In Line {line + 1}")
        return -1
    elif len(triangle_increment_list[line][0]) > len(triangle_increment_list[line][1]):
        Error(Output_Error_Color, f"Opening Triangle Increment Sign Was Used But Never Closed On Line {line + 1}")
        return -1
    elif len(triangle_increment_list[line][1]) > len(triangle_increment_list[line][0]):
        Error(Output_Error_Color, f"Closing Triangle Increment Sign Was Used But Never Opened On Line {line + 1}")
        return -1
    elif len(triangle_decrement_list[line][0]) > len(triangle_decrement_list[line][1]):
        Error(Output_Error_Color, f"Opening Triangle Decrement Sign Was Used But Never Closed On Line {line + 1}")
        return -1
    elif len(triangle_decrement_list[line][1]) > len(triangle_decrement_list[line][0]):
        Error(Output_Error_Color, f"Closing Triangle Decrement Sign Was Used But Never Opened On Line {line + 1}")
        return -1
    elif len(triangle_out_list[line][0]) > len(triangle_out_list[line][1]):
        Error(Output_Error_Color, f"Opening Triangle Print Out Sign Was Used But Never Closed On Line {line + 1}")
        return -1
    elif len(triangle_out_list[line][1]) > len(triangle_out_list[line][0]):
        Error(Output_Error_Color, f"Closing Triangle Print Out Sign Was Used But Never Opened On Line {line + 1}")
        return -1
    elif len(triangle_twice_list[line][0]) > len(triangle_twice_list[line][1]):
        Error(Output_Error_Color, f"Opening Triangle Twice Use Sign Was Used But Never Closed On Line {line + 1}")
        return -1
    elif len(triangle_twice_list[line][1]) > len(triangle_twice_list[line][0]):
        Error(Output_Error_Color, f"Closing Triangle Twice Use Sign Was Used But Never Opened On Line {line + 1}")
        return -1
    elif t_INSTRUCTION_BLOCK.replace("\\", "") in line_value[1:] and t_INSTRUCTION_BLOCK_UPDATE.replace("\\", "") in line_value[1:]:
        Error(Output_Error_Color, f"Instruction Block Was Not Properly Called as a Lined Function On Line {line + 1}")
        return -1
    elif line_value[0] == ENDLINE :
        Warned = Warning(Output_Warning_Color, f"Endline Character Is Used on Empty Line {line + 1}")
    elif "+++" in line_value :
        Warned = Warning(Output_Warning_Color, f"Consider Alternatives To Make The Long Increment Signs Smaller In Line {line + 1}")
    elif ">>>" in line_value :
        Warned = Warning(Output_Warning_Color, f"Consider Alternatives To Make The Long Arrows Smaller In Line {line + 1}")
    elif "----" in line_value :
        Warned = Warning(Output_Warning_Color, f"Consider Alternatives To Make The Long Decrement Signs Smaller In Line {line + 1}")
    elif t_INPUT_MODELESS in line_value[0:] :
        Warned = Warning(Output_Warning_Color, f"Using a Command \"{t_INPUT_MODELESS}\" Is Unnecessary On Line {line + 1}")
    return 0 if Warned else 1
def Transform(string: str, config):
  timer = time.perf_counter()
  string = string.strip()
  global Error, t_ENDLINE, position, Tape, Shell_Called, Shell_String, Current_Code_Line, Modifications, Modified, Increments_Triangles, Decrements_Triangles, OUT_Triangles
  global triangle_increment_list, triangle_decrement_list, triangle_out_list, Twice_Triangles
  if len(string) == 0: return ""
  Result = 0
  File = os.path.split(config)[1]
  if not os.path.exists(config):
      print("\033[31mNo Config File Has Been Found, Please Create One\033[0m")
      return f"\nFinished With Exit Code Of -1"
  if File != "BBF.config.json":
      print("\033[31mFile Is Not A BBF Config File\033[0m")
      return f"\nFinished With Exit Code Of -1"
  if File != "BBF.config.json":
      print("\033[31mFile Is Not A BBF Config File\033[0m")
  Tokens = []
  Warned = False
  lines = string.splitlines()
  string_computed = ""
  clipboard_string = ""
  Clipboard = ""
  Function_Tape = []
  Function_Position_Tape = 0
  True_String = string.splitlines()[0].replace(" ", "")
  True_String = True_String[True_String.find("#")] if True_String.find("#") != -1 else True_String
  Default_Value = 60_000
  HeaderDefination = False
  if True_String[0:2] == "//":
      if True_String[2] != "{":
          print (f"{Output_Error_Color} Expected A Opening Brace \"{{\" To Be Found On Line 1 {Reset}" )
          return -2
      if True_String[-1] != "}":
          print (f"{Output_Error_Color} Expected A Closing Brace \"}}\" To Be Found On Line 1 {Reset}" )
          return -2
      try:
          Default_Value = int(True_String[3:-1])
          if Default_Value <= 0:
            print (f"{Output_Error_Color} Cell Value Must Not Be Below Or Equal to 0 On Line 1 {Reset}" )
            return -2
          lines = lines[1:]
          HeaderDefination = True
      except:
          print ( f"{Output_Error_Color} Cell Value is Not a Valid Number On Line 1 {Reset}" )
          return -2
  for line, line_value in enumerate(lines):
      count_repeaters = line_value.count(t_REPEATER)
      copy = t_COPY_REPEATER.replace ( "\\", "" )
      count_copy_repeaters = line_value.count(copy)
      for _ in range (count_repeaters) :
        repeater = line_value.find ( t_REPEATER )
        line_value_list = list ( line_value )
        value = 0
        clipboard_string = clipboard_string.replace("\;", "")
        Clipboard = clipboard_string
        if len(line_value) > 0:
          if line_value[0] == t_SHELL_ENTER.replace("\\", "") or line_value[0] == t_SHELL_ENTER_2.replace("\\", ""):
              value = 1
        clipboard_string = line_value[value:repeater]
        if len(clipboard_string) == 0:
            Result, Warned = Repeater_Warn(line)
        line_value_list[repeater] = line_value[value : repeater]
        lines[line] = ''.join ( line_value_list )
        line_value = ''.join(line_value_list)
      for _ in range (count_copy_repeaters):
          value = 0
          repeater_copy = line_value.find(copy)
          if len(line_value) > 0:
            if line_value[0] == t_SHELL_ENTER.replace ( "\\", "" ) or line_value[0] == t_SHELL_ENTER_2.replace ( "\\", "" ) :
                value = 1
          clipboard_string = line_value[value:repeater_copy]
          Clipboard = clipboard_string
          line_value = line_value[repeater_copy + len(copy):]
      if t_PASTE_REPEATER in line_value:
         line_value = line_value.replace(t_PASTE_REPEATER.replace("\\", ""), Clipboard)
      if len(line_value) > 0:
        if line_value[0] == t_INSTRUCTION_BLOCK.replace("\\", ""):
            Function_Tape.append(line_value[1:-1])
            line_value = ""
      string_computed += line_value + "\n"
  with open(config, "r") as f:
      data = json.load(f)
      if data["Processing"]["Redundant Trashout"]["Enabled"]:
          with open( "./json/Redundant.json", "r" ) as f_trash:
              data_redundant = json.load (f_trash)
              for redundant in data_redundant["Redundant"]:
                 string = string.replace(redundant, "")
              lines = string.splitlines()
              for line in lines:
                  if len(line) > 0:
                    if line[0] == ";":
                        line = line.replace ( ";", "\n" )
      if data["Processing"]["Simplification"]["Enabled"]:
          with open( "./json/Replacements.json", "r" ) as f2:
              data2 = json.load(f2)
              for target, replacement in data2.items():
                string = string.replace(target, replacement)
  lexer.input(string)
  for _ in range(len(string)):
     tok = lexer.token()
     if not tok : break
     if tok.type == "INSTRUCTION_BLOCK_USE":
         lexer2.input(Function_Tape[Function_Position_Tape])
         while True:
             tok2 = lexer2.token()
             if not tok2 : break
             if tok2.type == "INSTRUCTION_BLOCK_USE":
                 print (f"{Output_Error_Color} Cannot Mention The Instruction Block Use Again, When Defining a Function On Line {tok2.lineno}{Reset}\n\nFinished With Exit Code Of -1" )
                 return Result
             Tokens.append(tok2)
         continue
     elif tok.type == "INSTRUCTION_BLOCK_MOVE_INCREMENT":
         Function_Position_Tape += 1
         if Function_Position_Tape >= len(Function_Tape):
             print (f"{Output_Error_Color} Cannot Exceed The Function Tape Limit When Using Instruction Increment Move On Line {tok.lineno}, Please Record More Functions{Reset}\n\nFinished With Exit Code Of -1" )
             return Result
         continue
     elif tok.type == "INSTRUCTION_BLOCK_MOVE_DECREMENT":
         Function_Position_Tape -= 1
         if Function_Position_Tape < 0:
             print (f"{Output_Error_Color} Cannot Go Further Down The Function Tape When Using Instruction Decrement Move On Line {tok.lineno}{Reset}\n\nFinished With Exit Code Of -1" )
             return Result
         continue
     Tokens.append(tok)
  Tape = [0] * Default_Value
  position = 0
  try: ErrorOutput = Error[1].replace("\n", "")
  except: ErrorOutput = None
  if Error[0] == -1:
      print(f"{Output_Error_Color} Unknown Character Called " + fr'"{ErrorOutput}"' + f" at Line {Error[2]}{Reset}\n\nFinished With Exit Code Of -1")
      return Result
  Current_Code_Line = 1
  lines = string.splitlines()
  for line, line_value in enumerate(lines):
      try:
        Result = Error_Handler(line, line_value, Tokens)
      except IndexError: Result = None
      if Result == -1:
          Color = "\033[4;32m"
          if Result == 0 or Warned : Color = "\033[4;33m"
          elif Result == -1 : Color = "\033[4;31m"
          print ( f"\n{Color}Finished With Exit Code Of {Result if not Warned else 0}{Reset}" )
          return
  def Output(pos, end, Shell_String, Modified, shell=False, Modifications=None):
      if shell:
         Shell_String += chr(Tape[pos])
      if Modifications:
         Modified.append(pos)
      if Modifications or shell:
          return Shell_String, Modified
      try: print ( chr ( Tape[pos] ) ) if end is True else print ( chr ( Tape[pos] ), end = "" )
      except UnicodeEncodeError : print ( "Cannot Encode" )
      return Shell_String, Modified
  def find_column (string, token) :
      line_start = string.rfind ( '\n', 0, token.lexpos ) + 1
      return (token.lexpos - line_start) + 1
  def Compile ( token, lines, current_line, prev_current_line) :
      global position, Tape, Shell_Called, Shell_String, Modifications, Modified, Increments_Triangles, Decrements_Triangles, OUT_Triangles, Twice_Triangles
      token_line = token.lineno
      token_type = token.type
      Display_Line = current_line + 1
      if position >= len(Tape) :
          print (f"{Output_Error_Color} Surpassed The Tape Limit Which is {len(Tape)} Memory Blocks, In Line {Display_Line}{Reset}" )
          return -2
      if position < 0:
          print (f"{Output_Error_Color} Position Cannot Be Negative Number. Use the Limit Operator if You Want to Go On the Last Memory Block, In Line {Display_Line}{Reset}" )
          return -2
      if Tape[position] < 0:
          print (f"{Output_Error_Color} Memory Block Cannot Be a Negative Number, In Line {Display_Line}{Reset}" )
          return -2
      if token_type == "INCREMENT_TRIANGLE_CLOSING" and Increments_Triangles <= 0:
          print (f"{Output_Error_Color} Cannot Close a Increment Triangle Sign Due to It Not Existing, In Line {Display_Line}{Reset}" )
          return -2
      if token_type == "DECREMENT_TRIANGLE_CLOSING" and Decrements_Triangles <= 0:
          print (f"{Output_Error_Color} Cannot Close a Decrement Triangle Sign Due to It Not Existing, In Line {Display_Line}{Reset}" )
          return -2
      if token_type == "__OUT__TRIANGLE_CLOSING" and OUT_Triangles <= 0:
          print (f"{Output_Error_Color} Cannot Close a Print Out Triangle Sign Due to It Not Existing, In Line {Display_Line}{Reset}" )
          return -2
      if token_type == "TWICE_TRIANGLE_CLOSING" and Twice_Triangles <= 0:
          print (f"{Output_Error_Color} Cannot Close a Twice Use Triangle Sign Due to It Not Existing, In Line {Display_Line}{Reset}" )
          return -2
      if current_line != prev_current_line or len (lines[current_line]) == 0 :
          if Shell_Called :
              os_system( Shell_String )
              Shell_Called = False
              Shell_String = ""
          if Modifications :
              for pos in Modified :
                  Tape[pos] = 0
              Modified = []
              Modifications = False
          prev_current_line += 1
      if "INC_ARROW_" in token_type:
          try:
            position += int(token_type[-1]) if "ARROW_CIRCLED" not in token_type else Tape[position]
          except:
              print (f"{Output_Error_Color} Cannot Move Beyond the Memory Tape ({len(Tape)} Elements) On Line {Display_Line}{Reset}" )
              return -2
      elif "DEC_ARROW_" in token_type:
          try:
            position -= int(token_type[-1]) if "ARROW_CIRCLED" not in token_type else Tape[position]
          except:
              print (f"{Output_Error_Color} Cannot Move Beyond the Memory Tape ({len(Tape)} Elements) On Line {Display_Line}{Reset}" )
              return -2
      elif "__INCREMENT__" in token_type:
          Tape[position] += int(token_type[0])
      elif "__DECREMENT__" in token_type:
          Tape[position] += int(token_type[0])
      elif "__ARROW__" in token_type:
          try:
             position += 1 if "INCREMENT__ARROW" in token_type else -1
             Tape[position] += 1 if "ARROW__INCREMENT" in token_type else -1
          except:
              print (f"{Output_Error_Color} Cannot Move Beyond the Memory Tape ({len(Tape)} Elements) On Line {Display_Line}{Reset}" )
              return -2
      elif token_type == "PI":
          Tape[position] = 3
      elif "INCREMENT_CIRCLED" in token_type or "DECREMENT_CIRCLED" in token_type:
            Area1 = position + 1
            Area2 = position - 1
            if position == 0:
                Area1 = position + 1
                Area2 = position + 2
            elif position == len(Tape) - 1:
                Area1 = position - 1
                Area2 = position - 2
            val = int(token_type[-1]) if "INCREMENT_CIRCLED" in token_type else -int(token_type[-1])
            Tape[position] += val
            Tape[Area1] += val
            Tape[Area2] += val
      elif "OUT_CIRCLED" in token_type:
          if "ESCAPE" not in token_type:
            Area1 = position + 1
            Area2 = position - 1
            if position == 0:
                Area1 = position + 1
                Area2 = position + 2
            elif position == len(Tape) - 1:
                Area1 = position - 1
                Area2 = position - 2
            for i in (Area1, position, Area2):
                try: print(chr(Tape[i])) if "END" in token_type else print (chr(Tape[i]), end = "")
                except UnicodeEncodeError: print ( "Cannot Encode" )
            return None
          try: print (chr(Tape[position])) if "END" in token_type else print (chr(Tape[position]), end = "" )
          except UnicodeEncodeError: print ( "Cannot Encode" )
      elif "OUT" in token_type and "__OUT__" not in token_type:
          Newline = True
          if "_WITHOUT_NEWLINE" in token_type:
              Newline = False
          if "INCREMENT_" in token_type:
              Tape[position] += 1
          elif "DECREMENT_" in token_type:
              Tape[position] -= 1
          Shell_String, Modified = Output ( position, Newline, Shell_String, Modified, Shell_Called, Modifications )
      elif "INPUT" in token_type:
          if Shell_Called and token_type != "INPUT_MODELESS" :
              command: str = input ( "$ " )
              os_system (command)
              return -1
          byte: bytes = input ( ">> " )
          Tape[position] = ord ( byte[0] )
      elif "SHELL_ENTER" in token_type:
          if (lines[token_line - 1][0] != token.value) or Shell_Called :
              print (f"{Output_Error_Color} Shell Lined Function Was Called Later On the Line {Display_Line}{Reset}" )
              return f"\nFinished With Exit Code Of -1"
          Shell_Called = True
          if token_type == "SHELL_ENTER_2" : Modifications = True
      elif "WAIT" in token_type:
          val = 1000 if token_type == "WAIT" else 1
          sleep(Tape[position] / val)
      elif token_type == "CELL_APPEND":
          Tape.append(0)
          position = max(min(position, len(Tape) - 1), 0)
      elif token_type == "CELL_REMOVE":
          Tape.pop(Tape[-1])
          position = max(min(position, len(Tape) - 1), 0)
      elif token_type == "STARTUP": position = 0
      elif token_type == "LIMIT": position = len(Tape) - 1
      elif token_type == "RESET": Tape[position] = 0
      elif token_type == "INCREMENT_TRIANGLE_OPENING":
          Increments_Triangles += 1
      elif token_type == "INCREMENT_TRIANGLE_CLOSING":
          Increments_Triangles -= 1
      elif token_type == "DECREMENT_TRIANGLE_OPENING":
          Decrements_Triangles += 1
      elif token_type == "DECREMENT_TRIANGLE_CLOSING":
          Decrements_Triangles -= 1
      elif token_type == "__OUT__TRIANGLE_OPENING":
          OUT_Triangles += 1
      elif token_type == "__OUT__TRIANGLE_CLOSING":
          OUT_Triangles -= 1
      elif token_type == "TWICE_TRIANGLE_OPENING":
          Twice_Triangles += 1
      elif token_type == "TWICE_TRIANGLE_CLOSING":
          Twice_Triangles -= 1
      if "_TRIANGLE_" not in token_type and (Increments_Triangles + Decrements_Triangles + OUT_Triangles > 0):
        Tape[position] += Increments_Triangles
        Tape[position] -= Decrements_Triangles
        Newline = False
        for i in range(OUT_Triangles): Shell_String, Modified = Output ( position, Newline, Shell_String, Modified, Shell_Called, Modifications )
  Shell_Called = False
  Shell_String = ""
  Modifications = []
  Modified = False
  current_line = 1 if HeaderDefination else 0
  Increments_Triangles = 0
  Decrements_Triangles = 0
  OUT_Triangles = 0
  Twice_Triangles = 0
  for token in Tokens:
      prev_current_line = current_line
      if token.type == "ENDLINE": current_line += 1
      for _ in range(Twice_Triangles + 1):
        if "TWICE_TRIANGLE_CLOSING" not in token.type:
           Error = Compile(token, lines, current_line, prev_current_line)
           if Error == -2:
               return f"\nFinished With Exit Code Of -1"
        #elif "TWICE_TRIANGLE_CLOSING" in token.type: Twice_Triangles -= 1
  Color = "\033[4;32m"
  if Result == 0 or Warned: Color = "\033[4;33m"
  elif Result == -1: Color = "\033[4;31m"
  else: Result = 1
  print(f"\n\n{Color}Finished With Exit Code Of {Result if not Warned else 0}{Reset}")
  print(f"Finished With Time Of {time.perf_counter() - timer} Seconds")


tokens = (
    'ENDLINE',
    'NUMBER',
    'FUNCTION',
    'INC_ARROW_1',
    'INC_ARROW_2',
    'INC_ARROW_3',
    "INC_ARROW_4",
    'DEC_ARROW_1',
    'DEC_ARROW_2',
    'DEC_ARROW_3',
    "DEC_ARROW_4",
    "INCREMENT_TRIANGLE_OPENING",
    "INCREMENT_TRIANGLE_CLOSING",
    "DECREMENT_TRIANGLE_OPENING",
    "DECREMENT_TRIANGLE_CLOSING",
    "TWICE_TRIANGLE_OPENING",
    "TWICE_TRIANGLE_CLOSING",
    "__OUT__TRIANGLE_OPENING",
    "__OUT__TRIANGLE_CLOSING",
    "INC_ARROW_CIRCLED",
    "DEC_ARROW_CIRCLED",
    "INCREMENT_CIRCLED_1",
    "DECREMENT_CIRCLED_1",
    "INCREMENT_CIRCLED_2",
    "DECREMENT_CIRCLED_2",
    "INCREMENT_CIRCLED_3",
    "DECREMENT_CIRCLED_3",
    "1__INCREMENT__",
    "1__DECREMENT__",
    "OUT",
    "OUT_WITHOUT_NEWLINE",
    "OUT_CIRCLED",
    "OUT_CIRCLED_END",
    "OUT_CIRCLED_ESCAPE",
    "OUT_CIRCLED_END_ESCAPE",
    "INPUT",
    "INPUT_MODELESS",
    "REPEATER",
    "PASTE_REPEATER",
    "COPY_REPEATER",
    "2__INCREMENT__",
    "3__INCREMENT__",
    "4__INCREMENT__",
    "2__DECREMENT__",
    "3__DECREMENT__",
    "4__DECREMENT__",
    "INCREMENT_OUT",
    "DECREMENT_OUT",
    "INCREMENT_OUT_WITHOUT_NEWLINE",
    "DECREMENT_OUT_WITHOUT_NEWLINE",
    "INCREMENT__ARROW__DECREMENT",
    "DECREMENT__ARROW__DECREMENT",
    "DECREMENT__ARROW__INCREMENT",
    "INCREMENT__ARROW__INCREMENT",
    "PI",
    "SHELL_ENTER",
    "SHELL_ENTER_2",
    "WAIT",
    "WAIT_SECONDS",
    "STARTUP",
    "LIMIT",
    "RESET",
    "INSTRUCTION_BLOCK",
    "INSTRUCTION_BLOCK_USE",
    "INSTRUCTION_BLOCK_MOVE_INCREMENT",
    "INSTRUCTION_BLOCK_MOVE_DECREMENT",
    "CELL_APPEND",
    "CELL_REMOVE",
)

t_ENDLINE = r"\;"
t_INC_ARROW_1 = r'\>'
t_INC_ARROW_2 = r'\»'
t_INC_ARROW_3 = r'\☛|\⋙'
t_INC_ARROW_4 = r'\⇨'
t_DEC_ARROW_1 = r'\<'
t_DEC_ARROW_2 = r'\«'
t_DEC_ARROW_3 = r'\☚|\⋘'
t_DEC_ARROW_4 = r'\⇦'
t_INC_ARROW_CIRCLED = r"\⧁"
t_DEC_ARROW_CIRCLED = r"\⧀"
t_INCREMENT_CIRCLED_1 = r"\⊕"
t_INCREMENT_CIRCLED_2 = r"\|\⊕\|"
t_INCREMENT_CIRCLED_3 = r"\(\⊕\)"
t_DECREMENT_CIRCLED_1 = r"\⊝"
t_DECREMENT_CIRCLED_2 = r"\|\⊝\|"
t_DECREMENT_CIRCLED_3 = r"\(\⊝\)"
t_OUT_CIRCLED = r"\㉧"
t_OUT_CIRCLED_END = r"\|\㉧\|"
t_OUT_CIRCLED_ESCAPE = r"\(\㉧\)"
t_OUT_CIRCLED_END_ESCAPE = r"\(\|\㉧\|\)"
t_1__INCREMENT__ = r"\+"
t_1__DECREMENT__ = r"\-"
t_OUT = r"\."
t_OUT_WITHOUT_NEWLINE = r"\|\.\|"
t_INPUT = r"\,"
t_INPUT_MODELESS = r"\|\,\|"
t_REPEATER = r"~"
t_PASTE_REPEATER = r"\|\:\|"
t_COPY_REPEATER = r"\|\±\|"
t_2__INCREMENT__ = r"\﹢"
t_3__INCREMENT__ = r"\＋"
t_4__INCREMENT__ = r"\➕"
t_2__DECREMENT__ = r"\﹣"
t_3__DECREMENT__ = r"\－"
t_4__DECREMENT__ = r"\➖"
t_INCREMENT_OUT = r"\∔"
t_DECREMENT_OUT = r"∸"
t_INCREMENT_OUT_WITHOUT_NEWLINE = r"\|\∔\|"
t_DECREMENT_OUT_WITHOUT_NEWLINE = r"\|\∸\|"
t_INCREMENT__ARROW__DECREMENT = r"\⇸"
t_DECREMENT__ARROW__DECREMENT = r"\⇷"
t_DECREMENT__ARROW__INCREMENT = r"\⥆"
t_INCREMENT__ARROW__INCREMENT = r"\⥅"
t_PI = r"\π"
t_SHELL_ENTER = r'\$'
t_SHELL_ENTER_2 = r'&'
t_WAIT = r'\§'
t_WAIT_SECONDS = r'\@'
t_STARTUP = r'\⬇'
t_LIMIT = r"\⬆"
t_RESET = r"\꛷"
t_INSTRUCTION_BLOCK = r"\⧆"
t_INSTRUCTION_BLOCK_USE = r"\⊡"
t_INSTRUCTION_BLOCK_MOVE_INCREMENT = r"\⊞"
t_INSTRUCTION_BLOCK_MOVE_DECREMENT = r"\⊟"
t_CELL_APPEND = r"\⌑"
t_CELL_REMOVE = r"\|\⌑\|"


def t_COMMENT(t):
     r'\#.*'
     pass

def t_INCREMENT_TRIANGLE_OPENING(t) :
    r'\{⨹'
    global triangle_increment_list
    if len(triangle_increment_list) < t.lineno:
        triangle_increment_list.append([[], []])
    triangle_increment_list[t.lineno - 1][0].append(t)
    return t


def t_INCREMENT_TRIANGLE_CLOSING ( t ) :
    r'⨹\}'
    global triangle_increment_list
    if len(triangle_increment_list) < t.lineno:
        triangle_increment_list.append([[], []])
    triangle_increment_list[t.lineno - 1][1].append(t)
    return t


def t_DECREMENT_TRIANGLE_OPENING(t) :
    r'\{⨺'
    global triangle_decrement_list
    if len(triangle_decrement_list) < t.lineno:
        triangle_decrement_list.append([[], []])
    triangle_decrement_list[t.lineno - 1][0].append(t)
    return t


def t_DECREMENT_TRIANGLE_CLOSING ( t ) :
    r'⨺\}'
    global triangle_decrement_list
    if len(triangle_decrement_list) < t.lineno:
        triangle_decrement_list.append([[], []])
    triangle_decrement_list[t.lineno - 1][1].append(t)
    return t

def t___OUT__TRIANGLE_OPENING(t) :
    r'\{◬'
    global triangle_out_list
    if len(triangle_out_list) < t.lineno:
        triangle_out_list.append([[], []])
    triangle_out_list[t.lineno - 1][0].append(t)
    return t


def t___OUT__TRIANGLE_CLOSING ( t ) :
    r'◬\}'
    global triangle_out_list
    if len(triangle_out_list) < t.lineno:
        triangle_out_list.append([[], []])
    triangle_out_list[t.lineno - 1][1].append(t)
    return t


def t_TWICE_TRIANGLE_OPENING(t) :
    r'\{⟁'
    global triangle_twice_list
    if len(triangle_twice_list) < t.lineno:
        [triangle_twice_list.append([[], []]) for i in range(t.lineno)]
    triangle_twice_list[t.lineno - 1][0].append(t)
    return t


def t_TWICE_TRIANGLE_CLOSING ( t ) :
    r'⟁\}'
    global triangle_twice_list
    if len(triangle_twice_list) < t.lineno:
        triangle_twice_list.append([[], []])
    triangle_twice_list[t.lineno - 1][1].append(t)
    return t


def t_newline ( t ) :
    r'\n+'
    t.lexer.lineno += len (t.value)

t_ignore = ' \t'

def t_error (t):
    global Error
    Error = [-1, t.value, t.lineno]
    t.lexer.skip ( 1 )


lexer = lex.lex(debug=False)
lexer2 = lex.lex(debug=False)