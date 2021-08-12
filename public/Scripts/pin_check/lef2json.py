import os
import json
import sys
import re
from log import Logging
from utils import regexExtraction, write, jsonWrite,check_file, read,jsonRead, makeDirs

def readlef(filename):
    """
    Read lef file and return lef file data as string 

    Usage::
        >>> import lef2json
        >>> lef_data = lef2json.readlef("file_name.lef")
    
    :param: filename: Filename of the lef file
    :returns: It will return lef file data
    :rtype: lef file data as string  

    """    
    try:
        content = read(filename)
        Logging.message("INFO", f"READING THE LEF FILE AND EXTRACTING INFORMATION\n    {filename}")
    except:
        Logging.message("ERROR", f"COULDN'T READ THE LEF FILE\n    {filename}")
    return content

def getDirection(content, PinName):
    """
    This function will Find and return the pin direction from given pin content
    Usage::
        >>> import lef2json
        >>> direction = lef2json.getDirection("lef_pin_content","pin_name")
    
    :param: content: PIN A
                        ...
                        DIRECTION INPUT;
                        ...
                     END A
    :param: PinName: name of the pin.
    :returns: It will return pin direction 
    :rtype: direction as string  
    
    """      
    regexDir = r"^(\s+)?(\bDIRECTION\b)\s+(.*)"
    Dir = re.search(regexDir, content, re.MULTILINE)
    if Dir:
        Dir = Dir.group(3)
    else :
        Dir = ""
        Logging.message("WARNING", f"COULDN'T FOUND PIN DIRECTION FOR PIN\n    {PinName}")
    return Dir
   

def ExtractCellInfo(content,MacroName,filename):
    """
    This function will extract the pin information from cell data.

    Usage::
        >>> import lef2json
        >>> lef2json.ExtractCellInfo("CELL_DATA","CELL_NAME","FILE_NAME")

    :param: content: cell data from which pin information will be extracted.
    :param: MacroName: cell name
    :param: filename : lef file name
    :returns: CellDic: pin data as json dictionary
    
    """    
    Logging.message("INFO", f"EXTRACTING PORT INFORMATION FOR <{MacroName}> FROM THE LEF FILE\n    {filename}")    
    CellDic = {}
    PortDic = {}
    regexCellPIN = r"^(\s+)?PIN\s+(.*)"
    for CellContent in content:
        CellPIN = regexExtraction(regexCellPIN, CellContent)
        if CellPIN:
            for Name in CellPIN:
                PIN = Name.strip().split()[1].strip()
                # Regex For Extracting PIN information If pin define as A[0]
                if "[" in PIN:
                    split_text =  PIN.split("[")
                    PIN_REGEX = split_text[0] + "\[" + split_text[1].split("]")[0] + "\]"
                    regexPinInfo = r"^(\s+)?PIN\s+(%s$)(.|\n)*?(^(\s+)?END\s+(%s$))" %(PIN_REGEX,PIN_REGEX)
                # Regex For Extracting PIN information If pin define as A
                else:
                    regexPinInfo = r"^(\s+)?PIN\s+(%s$)(.|\n)*?(^(\s+)?END\s+(%s$))" %(PIN,PIN)

                PinInfo = regexExtraction(regexPinInfo, CellContent)
                for Name in PinInfo:
                    DIRECTION = getDirection(Name, PIN)

                # Remove NON-WORD Characters 
                DIRECTION = re.sub(r"\W+",'',DIRECTION)

                # Create PIN dictionary
                CellDic[PIN] = PIN.strip()
                PortDic["PortName"] = PIN.strip()
                PortDic["PortDirection"] = DIRECTION.strip()
                CellDic[PIN] = PortDic
                PortDic = {}
        else :
            Logging.message("WARNING", f"COULDN'T FOUND PIN INSIDE\n    {MacroName}")
    return CellDic


# Create Json From LEF file
def lefJson(filename):
    """
    This function will extract the cell information from lef file.

    Usage::
        >>> import lef2json
        >>> lef2json.lefJson("FILE_NAME")

    :param: filename : lef file name
    :returns: lefDic: lef file data as json dictionary
    :returns: FileContent: lef file data as string 
    
    """
    content = readlef(filename)
    FileContent = content
    # Logging.message("INFO", f"CONVERTING JSON FROM THE LEF FILE\n    {filename}")
    lefDic = {}
    regexMacroCell = r"^(\s+)?MACRO\s+(.*)"
    MacroCell = regexExtraction(regexMacroCell, content)
    if MacroCell:
        # Create Cell Dictionary 
        for Name in MacroCell:
            MacroName = Name.strip().split()[1].strip()
            regexMacroContent = r'^(\s+)?MACRO\s+%s$(.|\n)*?(^(\s+)?END\s+%s$)' %(MacroName,MacroName)
            MacroContent = regexExtraction(regexMacroContent, content)
            CellDic = ExtractCellInfo(MacroContent,MacroName,filename)
            lefDic[MacroName] = CellDic   
    else :
        Logging.message("WARNING", f"COULDN'T FOUND MACRO IN THE LEF FILE\n    {filename}")
    return lefDic, FileContent

# Extract File Names From LEF PATH
def getFiles(PATH):
    """
    This function will extract the file name and create a file list from given path.

    Usage::
        >>> import lef2json
        >>> lef2json.getFiles("LIBRARY_PATH")

    :param: PATH: library path from where file list will be created.
    :returns: file list as list
    
    """
    FileList = []
    for path, subdirs, files in os.walk(PATH): 
        for fileName in files:       
            FileList.append(os.path.join(path,fileName))
    return FileList

# Update and Merge Previous JSON Dictionary 
def merge_dict(prev_dic, new_dic):
    """
    This function will update and merge the previous json data with new json data.

    Usage::
        >>> import lef2json
        >>> lef2json.merge_dict("PREVIOUS_JSON_DATA", "NEW_JSON_DATA")

    :param: prev_dic: previous json data
    :param: new_dic: new json data
    :returns: Updated json data as dictionary
    
    """   
    CellKey_prev = [*prev_dic.keys()]
    CellKey_new = [*new_dic.keys()]
    for CellKey in CellKey_new:
        if CellKey in CellKey_prev:
            prev_dic[CellKey].update(new_dic[CellKey])
        else:
            prev_dic[CellKey] = new_dic[CellKey]
    return prev_dic

# Create LEF JSON Dictionary and wirte into .temp folder
def LefJsonMain(PATH,IP_TYPE):
    """
    This function will create and update the json data for each lef file from
    given library path.
    Json data will be saved in <RUN_DIRECTORY>/.temp/lef.json path.

    Usage::
        >>> import lef2json
        >>> lef2json.LefJsonMain("LIBRARY_PATH","IP_TYPE")

    :param: PATH: library path for lef files
    :param: IP_TYPE: ip type example: memory,io,logic etc
    :returns: None

    """ 
    isFile = os.path.isfile(PATH)
    if not isFile:
        ALL_LEF =""
        lefDicMerge = {}
        prevDic = {}
        lefJsonContent = {}
        lefFileContent = {}
        FileList = getFiles(PATH)
        if len(FileList) == 0:
            Logging.message("WARNING", f"COULDN'T FOUND LEF FILE INSIDE\n    {PATH}")
            
        for fileName in FileList:
            lefDic, FileContent = lefJson(fileName)
            # For IO,LOGIC,AMS etc. Create JSON Dictionary with FileName
            if IP_TYPE.strip() != "MEMORY":
                lefJsonContent[os.path.basename(fileName)] = lefDic
                try:
                    prevDic = jsonRead(".temp/lef")
                    lefDicMerge = merge_dict(prevDic, lefJsonContent)
                    jsonWrite(".temp/lef", lefDicMerge)
                except:
                    prevDic = {} 
                    lefDicMerge = lefJsonContent      
                    jsonWrite(".temp/lef", lefDicMerge)
            # For Memory Merge all lef into ALL.lef JSON dictionary
            else: 
                lefJsonContent["ALL.lef"] = lefDic
                try:
                    prevDic = jsonRead(".temp/lef")
                    lefDicMerge = merge_dict(prevDic, lefJsonContent)
                    jsonWrite(".temp/lef", lefDicMerge)
                except:
                    prevDic = {} 
                    lefDicMerge = lefJsonContent      
                    jsonWrite(".temp/lef", lefDicMerge)

            # Create JSON Dictionary with filename for same view Comparison
            lefFileContent[os.path.basename(fileName)] = lefDic
            try:
                prevFileDic = jsonRead(".temp/lefFile")
                lefFileDicMerge = merge_dict(prevFileDic, lefFileContent)
                jsonWrite(".temp/lefFile", lefFileDicMerge)
            except:
                prevFileDic = {} 
                lefFileDicMerge = lefFileContent      
                jsonWrite(".temp/lefFile", lefFileDicMerge)   

            # MERGE FILES INTO ALL.lef
            if IP_TYPE.strip() == "MEMORY":
                ALL_LEF = ALL_LEF + f"# FILE : {os.path.basename(fileName)}\n" + FileContent + "\n\n"
        
        if ALL_LEF.strip(): 
            # Logging.message("INFO", f"Writing file\n    {os.path.join(PATH,'ALL.lef')}")
            with open(os.path.join(PATH,"ALL.lef"), 'w') as f:
                f.write(ALL_LEF)         
    else:
        Logging.message("ERROR", f"EXPECTED PATH BUT FOUND FILE\n    {PATH}")


