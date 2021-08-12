import os
import json
import sys
import re
from log import Logging
from utils import regexExtraction, write, jsonWrite,check_file, read,jsonRead, makeDirs

# Read LIB file From LIB PATH    
def readlib(filename):
    """
    This function will read the lib file and returns it's data.

    Usage::
        >>> import lib2json
        >>> lib2json.readlib("FILE_NAME")

    :param: filename: .lib file name.
    :returns: file data as string
    
    """
    try:
        content = read(filename)
        Logging.message("INFO", f"READING THE LIB FILE AND EXTRACTING INFORMATION\n    {filename}")
    except:
        Logging.message("ERROR", f"COULDN'T READ THE LIB FILE\n    {filename}")
    return content

# Extract PIN Direction 
def getDirection(content, PinName):
    """
    This function will extract the pin direction from pin data.

    Usage::
        >>> import lib2json
        >>> lib2json.getDirection("PIN_DATA","PIN_NAME")

    :param: content: pin data from which pin direction will be extracted.
    :param: PinName: name of the pin.
    :returns: pin direction as string
    
    """
    regexDir = r"\bdirection\b(\s+)?(\:(\s+)?(.*))"    
    Dir = re.search(regexDir, content, re.MULTILINE)
    if Dir:
        Dir = Dir.group(4).strip()
    else :
        Dir = ""
        Logging.message("WARNING", f"COULDN'T FOUND PIN DIRECTION FOR PIN\n    {PinName}")
    return Dir

# Extract Pin and Direction from Cell Content
def ExtractPortInfo(content,CellName,filename):
    """
    This function will create json data for ports from given cell data.

    Usage::
        >>> import lib2json
        >>> lib2json.ExtractPortInfo("CELL_DATA","CELL_NAME","FILE_NAME")

    :param: content: cell data from which port data will be extracted.
    :param: CellName: cell name of the given cell data
    :param: filename: .lib file name
    :returns: port json data as dictionary
    
    """
    Logging.message("INFO", f"EXTRACTING PORT INFORMATION FOR <{CellName}> FROM THE LIB FILE\n    {filename}")
    CellDic = {}
    PortDic = {}
    regexCellPIN = r"^(\s+)?\b(pin|pg_pin)\b(\s+)?(\((.*)\))"
    for CellContent in content:
        CellPIN = re.finditer(regexCellPIN, CellContent, re.M)
        if CellPIN:
            for Name in CellPIN:
                PIN = Name.group(5).strip() 
                DIRECTION = getDirection(CellContent, PIN) 
                # Remove NON-WORD Characters 
                DIRECTION = re.sub(r"\W+",'',DIRECTION)
                # Create PIN dictionary
                CellDic[PIN] = PIN
                PortDic["PortName"] = PIN.strip()
                PortDic["PortDirection"] = DIRECTION.strip()
                CellDic[PIN] = PortDic
                PortDic = {}
                
        else :
            Logging.message("WARNING", f"COULDN'T FOUND PIN INSIDE\n    {CellName}")
    return CellDic


def remove_test_cell(content):
    """
    This function will remove the test_cell data from given cell data.

    Usage::
        >>> import lib2json
        >>> lib2json.remove_test_cell("CELL_DATA")

    :param: content: cell data from which test_cell data will be removed.
    :returns: cell data as string
    
    """
    cp_test_cell_info = ""
    new_content = ""
    test_cell_info = []
    count_brace = 0
    flag = False
    for lineNum, line in enumerate(content.split("\n"),start=1):
        test_cell_line = re.search(r"^(\s+)?(\btest_cell\b)(.*)(?<={)", line,re.M)
        if test_cell_line:
            count_brace = 1
            flag = True
        
        if count_brace > 0 and flag:
            cp_test_cell_info = cp_test_cell_info + "\n" + line
        
        if not flag:
            new_content = new_content + "\n" + line

        new_brace = re.search(r"\{",line,re.M)
        if new_brace and not test_cell_line and flag:
            count_brace = count_brace + 1
        
        end_brace = re.search(r"\}",line,re.M)
        if end_brace:
            if flag:
                count_brace = count_brace - 1
                if count_brace == 0:
                    test_cell_info.append(cp_test_cell_info)
                    cp_test_cell_info = ""
                    flag =False  
    return new_content


def Grep_Pin_Info(content):
    """
    This function will create a list of port data from given cell data.

    Usage::
        >>> import lib2json
        >>> lib2json.Grep_Pin_Info("CELL_DATA")

    :param: content: cell data from which port data will be extracted.
    :returns: port data as list
    
    """
    cp_pin_info = ""
    pin_info = []
    count_brace = 0
    flag = False
    for lineNum, line in enumerate(content.split("\n"),start=1):
        pin_line = re.search(r"^(\s+)?(\b(pin|pg_pin)\b)(.*)(?<={)", line,re.M)
        if pin_line:
            count_brace = 1
            flag = True
        
        if count_brace > 0 and flag:
            cp_pin_info = cp_pin_info + "\n" + line

        new_brace = re.search(r"\{",line,re.M)
        if new_brace and not pin_line and flag:
            count_brace = count_brace + 1
        
        end_brace = re.search(r"\}",line,re.M)
        if end_brace:
            if flag:
                count_brace = count_brace - 1
                if count_brace == 0:
                    pin_info.append(cp_pin_info)
                    cp_pin_info = ""
                    flag =False
    return pin_info

def Grep_Cell_Info(content):
    """
    This function will create a list of cell data from given .lib file data.

    Usage::
        >>> import lib2json
        >>> lib2json.Grep_Cell_Info("LIB_FILE_DATA")

    :param: content: .lib file data from which cell data will be extracted.
    :returns: cell data as list
    
    """
    cp_cell_info = ""
    cell_info = []
    count_brace = 0
    flag = False
    for lineNum, line in enumerate(content.split("\n"),start=1):
        cell_line = re.search(r"^(\s+)?(\bcell\b)(.*)(?<={)", line,re.M)
        if cell_line:
            count_brace = 1
            flag = True
        
        if count_brace > 0 and flag:
            cp_cell_info = cp_cell_info + "\n" + line

        new_brace = re.search(r"\{",line,re.M)
        if new_brace and not cell_line and flag:
            count_brace = count_brace + 1
        
        end_brace = re.search(r"\}",line,re.M)
        if end_brace:
            if flag:
                count_brace = count_brace - 1
                if count_brace == 0:
                    cell_info.append(cp_cell_info)
                    cp_cell_info = ""
                    flag =False
    return cell_info    

# Create Json From LIB file
def libJson(filename):
    """
    This function will create json data from given file. 

    Usage::
        >>> import lib2json
        >>> lib2json.libJson("FILE_NAME")

    :param: filename: name of the .lib file for which json will be created
    :returns: libDic: json data as dictionary
    :returns: FileContentfile: file data as string
    
    """
    content = readlib(filename)
    FileContent = content
    # Logging.message("INFO", f"CONVERTING JSON FROM THE LIB FILE\n    {filename}")
    libDic = {}
    Cell = Grep_Cell_Info(content)
    if Cell:
        # Create Cell Dictionary 
        for CellInfo in Cell:
            CellInfo = remove_test_cell(CellInfo)
            regexCellName = r"^(\s+)?\bcell\b(\s+)?(\((.*)\)(\s+)?\{)"
            CellName_extract = re.finditer(regexCellName, CellInfo, re.M)
            for Name in CellName_extract:
                CellName = Name.group(4).strip()
                CellName = re.sub(r"\'",'',CellName)
                CellName = re.sub(r'\"','',CellName)
                
            PortInfo = Grep_Pin_Info(CellInfo)
            if PortInfo:
                CellDic = ExtractPortInfo(PortInfo,CellName,filename)
                libDic[CellName] = CellDic
            else:
                Logging.message("WARNING", f"COULDN'T FOUND PIN INSIDE\n    {CellName}")

    else :
        Logging.message("WARNING", f"COULDN'T FOUND CELL IN THE LIB FILE\n    {filename}")
    return libDic, FileContent

# Extract File Names From LIB PATH
def getFiles(PATH):
    """
    This function will extract the file name and create a file list from given path.

    Usage::
        >>> import lib2json
        >>> lib2json.getFiles("LIBRARY_PATH")

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
        >>> import lib2json
        >>> lib2json.merge_dict("PREVIOUS_JSON_DATA", "NEW_JSON_DATA")

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

# Create LIB JSON Dictionary and wirte into .temp folder
def LibJsonMain(PATH,IP_TYPE):
    """
    This function will create and update the json data for each .lib file from
    given library path. Json data will be created and updated for given cell name only.
    Json data will be saved in <RUN_DIRECTORY>/.temp path.

    Usage::
        >>> import lib2json
        >>> lib2json.LibJsonMain("LIBRARY_PATH", "IP_TYPE")

    :param: PATH: library path for .lib files
    :param: IP_TYPE: Ip type. Ex. IO,memory,logic etc.
    :returns: None

    """

    isFile = os.path.isfile(PATH)
    if not isFile:
        ALL_LIB = ""
        libDicMerge = {}
        prevDic = {}
        libJsonContent = {}
        libFileContent = {}
        FileList = getFiles(PATH)
        if len(FileList) == 0:
            Logging.message("WARNING", f"COULDN'T FOUND LIB FILE INSIDE\n    {PATH}")

        for fileName in FileList:
            libDic, FileContent = libJson(fileName) 
            # For IO,LOGIC,AMS etc. Create JSON Dictionary with FileName
            if IP_TYPE.strip() != "MEMORY": 
                libJsonContent[os.path.basename(fileName)] = libDic
                try:
                    prevDic = jsonRead(".temp/lib")
                    libDicMerge = merge_dict(prevDic, libJsonContent)
                    jsonWrite(".temp/lib", libDicMerge)
                except:
                    prevDic = {} 
                    libDicMerge = libJsonContent      
                    jsonWrite(".temp/lib", libDicMerge)
            # For Memory Merge all lib into ALL.lib JSON dictionary        
            else: 
                libJsonContent["ALL.lib"] = libDic
                try:
                    prevDic = jsonRead(".temp/lib")
                    libDicMerge = merge_dict(prevDic, libJsonContent)
                    jsonWrite(".temp/lib", libDicMerge)
                except:
                    prevDic = {} 
                    libDicMerge = libJsonContent      
                    jsonWrite(".temp/lib", libDicMerge)     

            # Create JSON Dictionary with filename for same view Comparison
            libFileContent[os.path.basename(fileName)] = libDic
            try:
                prevFileDic = jsonRead(".temp/libFile")
                libFileDicMerge = merge_dict(prevFileDic, libFileContent)
                jsonWrite(".temp/libFile", libFileDicMerge)
            except:
                prevFileDic = {} 
                libFileDicMerge = libFileContent      
                jsonWrite(".temp/libFile", libFileDicMerge) 

            # MERGE FILES INTO ALL.lib
            if IP_TYPE.strip() == "MEMORY":
                ALL_LIB = ALL_LIB + f"# FILE : {os.path.basename(fileName)}\n" + FileContent + "\n\n"
        
        if ALL_LIB.strip():  
            # Logging.message("INFO", f"Writing file\n    {os.path.join(PATH,'ALL.lib')}")
            with open(os.path.join(PATH,"ALL.lib"), 'w') as f:
                f.write(ALL_LIB)                   
    else:
        Logging.message("ERROR", f"EXPECTED PATH BUT FOUND FILE\n    {PATH}")

