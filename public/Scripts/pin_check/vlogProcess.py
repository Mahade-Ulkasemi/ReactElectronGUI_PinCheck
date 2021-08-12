import json
from log import Logging
from utils import regexExtraction, write, read, jsonWrite, jsonRead, check_file
import re
import sys
import os
import shutil

# Remove Comments and Unwanted content
def removeContentData(regex, content):
    """
    This function will remove unwanted content from given regular expression.
    """
    remove = regexExtraction(regex, content)  
    if remove:
        for cont in remove:
            content = content.replace(cont, "")
    return content

# Extract Module Name and Module Content
def regexExtractionModule(regex, content, opType):
    """
    This function will extract information from a given regular expression
    """
    updatedContent = []
    moduleList = []
    extractedContent = re.finditer(regex, content, re.M)
    if extractedContent:
        for matchNum, match in enumerate(extractedContent, start=1):
            updatedContent.append(match.group())
            if match.group(1):
                moduleList.append(match.group(1))
            if opType == "DEFINE_TRUE":
                if match.group(8):
                    moduleList.append(match.group(8))
                elif match.group(15):
                    moduleList.append(match.group(15))
            if opType == "DEFINE_FALSE":
                if match.group(13):
                    moduleList.append(match.group(13))
                elif match.group(25):
                    moduleList.append(match.group(25))
    return updatedContent, moduleList

def splitOverComma(content):
    """
    WILL split for electrical [5:0]in, in2, in3
    """
    for i in content.split('\n'):
        if re.match(r'^\w+\s+(\[.*:.*])?(\s+)?\w+(\s+)?,(\s+)?\w+', i):
            if i.split(' ')[0] != "":
                item = re.search('\w+\s+(\[.*:.*])?', i,re.MULTILINE)
                # WILL split for electrical [5:0]in, in2, in3
                p = ((';\n'+item.group()+' ').join(x.strip()
                                                   for x in re.split(',', i)))
                p += "\n"
                content = content.replace(i, p)
    return content

# Extract Port Information From Module Content
def portExtraction(content, verFile, moduleName, PortDataDic):   
    """
    This function will extract the port information from module content.

    """ 
    Logging.message(
        "INFO", f"EXTRACTING PORT INFORMATION FOR <{moduleName}> FROM THE VERILOG FILE\n    {verFile}")
    portName = ""
    portDir = ""
    portType = ""
    portWidth = ""
    PortDic = {}
    moduleDecSec = re.findall(r"module[^\)\;]*\)\;", content)
    if moduleDecSec:
        for index, mDecItem in enumerate(moduleDecSec):
            # Processing Module Declaration Sec
            new_string = " ".join(mDecItem.splitlines())
            new_string = re.sub(r"\)", "\n)", new_string)
            for ioPtr in ["input", "output", "inout"]:
                new_string = new_string.replace(ioPtr, f"\n{ioPtr}")
            moduleDecSec[index] = new_string
            content = content.replace(mDecItem, moduleDecSec[index])
    # Inserting All input,output, inout declaration in the new line
    for ioPtr in ["input", "output", "inout"]:
        content = content.replace(ioPtr, f"\n{ioPtr}")
    if moduleDecSec:
        for mDecItem in moduleDecSec:
            if re.search(r"^(input|output|inout)\s+", mDecItem,re.MULTILINE):
                for matchNum, match in enumerate(re.finditer(r"^(input|output|inout)\s+(.*?)(;|\n)", mDecItem, re.M), start=0):
                    portDir = ""
                    portDir = match.group(1).strip()
                    match2 = match.group(2).split(",")
                    match3 = re.search(
                        r"^(\w+\s+)?(signed\s+)?(\[.*:.*](\s+)?)?(\w+)", match2[0],re.MULTILINE)
                    if match3:
                        for Num, Name in enumerate(match2):

                            if Name.strip():
                                if Num == 0:
                                    portName = match3.group(5).strip()
                                else:
                                    portName = match2[Num].strip()
                                if match3.group(1):
                                    if match3.group(1).strip() != "signed":
                                        portType = match3.group(1).strip()
                                    else:
                                        portType = "wire"
                                else:
                                    portType = "wire"

                                if match3.group(3):
                                    portWidth = match3.group(3).strip()
                                else:
                                    portWidth = ""

                                if match3.group(1):
                                    if match3.group(1).strip() == "signed":
                                        portType = portType + " " + \
                                            match3.group(1).strip()
                                    elif match3.group(2):
                                        portType = portType + " " + \
                                            match3.group(2).strip()

                                portDic = {}
                                if portWidth:
                                    split_text = portWidth.split(":")
                                    bus_width = abs(int(split_text[0].split("[")[1]) - int(split_text[1].split("]")[0])) +1
                                    for i in range(bus_width):
                                        portName_array = portName + "[" + str(i) + "]"
                                        portDic["PortName"] = portName_array
                                        portDic["PortDirection"] = portDir
                                        portDic["PortType"] = portType
                                        PortDic[portName_array] = portDic
                                        portDic = {}
                                else:
                                    portDic["PortName"] = portName
                                    portDic["PortDirection"] = portDir
                                    portDic["PortType"] = portType                                    
                                    PortDic[portName] = portDic    
                                portName = ""
                                portType = ""
                                portWidth = ""

            else:
                for subM in moduleDecSec:
                    content = content.replace(subM, "")
                content = splitOverComma(content)

                for matchNum, match in enumerate(re.finditer(r"^(input|output|inout)\s+(.*?)(;|\n)", content, re.MULTILINE), start=0):
                    portDir = ""
                    portType = ""
                    portName = ""
                    portWidth = ""
                    portDir = match.group(1).strip()
                    match2 = match.group(2).split(",")
                    match3 = re.search(
                        r"^(\w+\s+)?(signed\s+)?(\[.*:.*](\s+)?)?(\w+)", match2[0],re.MULTILINE)

                    if match3:
                        for Num, Name in enumerate(match2):
                            if Name.strip():
                                if Num == 0:
                                    portName = match3.group(5).strip()
                                else:
                                    portName = match2[Num].strip()
                                if match3.group(1):
                                    if match3.group(1).strip() != "signed":
                                        portType = match3.group(1).strip()
                                    else:
                                        for Num2, Name2 in enumerate(match2):
                                            if Name.strip():
                                                if Num == 0:
                                                    portName_D = match3.group(
                                                        5).strip()
                                                else:
                                                    portName_D = match2[Num].strip(
                                                    )
                                                pattern = r"^(\w+\s+)(signed\s+)?(\[.*:.*](\s+)?)?" + \
                                                    r"(" + portName_D + r")" + \
                                                    r"(\s+)?(\;|\,)"

                                                for matchNum4, match4 in enumerate(re.finditer(pattern, content, re.M), start=0):
                                                    if match4.group(1):
                                                        if match4.group(1).strip() != portDir.strip():
                                                            portType = match4.group(
                                                                1).strip()
                                        if not portType:
                                            portType = "wire"
                                else:
                                    for Num2, Name2 in enumerate(match2):
                                        if Name.strip():
                                            if Num == 0:
                                                portName_D = match3.group(
                                                    5).strip()
                                            else:
                                                portName_D = match2[Num].strip(
                                                )
                                            pattern = r"^(\w+\s+)(signed\s+)?(\[.*:.*](\s+)?)?" + \
                                                r"(" + portName_D + r")" + \
                                                r"(\s+)?(\;|\,)"
                                            for matchNum4, match4 in enumerate(re.finditer(pattern, content, re.M), start=0):
                                                if match4.group(1):
                                                    if match4.group(1).strip() != portDir.strip():
                                                        portType = match4.group(
                                                            1).strip()
                                    if not portType:
                                        portType = "wire"

                                if match3.group(3):
                                    portWidth = match3.group(3).strip()
                                else:
                                    for Num2, Name2 in enumerate(match2):
                                        if Name.strip():
                                            if Num == 0:
                                                portName_D = match3.group(
                                                    5).strip()
                                            else:
                                                portName_D = match2[Num].strip(
                                                )
                                            pattern = r"^(\w+\s+)(signed\s+)?(\[.*:.*](\s+)?)?" + \
                                                r"(" + portName_D + r")" + \
                                                r"(\s+)?(\;|\,)"
                                            for matchNum4, match4 in enumerate(re.finditer(pattern, content, re.M), start=0):
                                                if match4.group(1):
                                                    if match4.group(1).strip() != portDir.strip():
                                                        if match4.group(3):
                                                            portWidth = match4.group(
                                                                3).strip()
                                                        else:
                                                            portWidth = ""

                                if match3.group(1):
                                    if match3.group(1).strip() == "signed":
                                        portType = portType + " " + \
                                            match3.group(1).strip()
                                    elif match3.group(2):
                                        portType = portType + " " + \
                                            match3.group(2).strip()
                                else:
                                    for Num2, Name2 in enumerate(match2):
                                        if Name.strip():
                                            if Num == 0:
                                                portName_D = match3.group(
                                                    5).strip()
                                            else:
                                                portName_D = match2[Num].strip(
                                                )
                                            pattern = r"^(\w+\s+)(signed\s+)?(\[.*:.*](\s+)?)?" + \
                                                r"(" + portName_D + r")" + \
                                                r"(\s+)?(\;|\,)"
                                            for matchNum4, match4 in enumerate(re.finditer(pattern, content, re.M), start=0):
                                                if match4.group(1):
                                                    if match4.group(1).strip() != portDir.strip():
                                                        if match4.group(2):
                                                            portType = portType + " " + \
                                                                match4.group(
                                                                    2).strip()
                                portDic = {}
                                if portWidth:
                                    split_text = portWidth.split(":")
                                    bus_width = abs(int(split_text[0].split("[")[1]) - int(split_text[1].split("]")[0])) +1
                                    for i in range(bus_width):
                                        portName_array = portName + "[" + str(i) + "]"
                                        portDic["PortName"] = portName_array
                                        portDic["PortDirection"] = portDir
                                        portDic["PortType"] = portType
                                        PortDic[portName_array] = portDic
                                        portDic = {}
                                else:
                                    portDic["PortName"] = portName
                                    portDic["PortDirection"] = portDir
                                    portDic["PortType"] = portType                                    
                                    PortDic[portName] = portDic    
                                portName = ""
                                portType = ""
                                portWidth = ""

                break
    else:
        Logging.message(
            "ERROR", f"COULDN'T FOUND MODULE SECTION ISIDE VERILOG FILE\n    {verFile}")

    if not PortDic:
        Logging.message("WARNING",f"COULDN'T FOUND PIN INSIDE\n    {moduleName}")
    PortDataDic[moduleName] = PortDic
    return PortDataDic

# Extract Module And Create JSON dictionary
def vLogModule(content, verFile, portData):
    PortDataDic = {}
    content_original = content
    modulePtr = r"^(module(\s+).*)(\s+)?\((.|\n)*?endmodule"
    content, moduleList = regexExtractionModule(modulePtr, content, "")
    if not content:
        Logging.message("ERROR", "COULDN'T FOUND ANY MODULE IN THE VERILOG FILE\n    %s" %
                        (verFile))
    
    moduleNameList = []
    for j in range(len(moduleList)):
        moduleNameList.append(moduleList[j].split("module")[1].strip())
    removeModule = []
    for CellName in moduleNameList:
        regexRemoveCell = r"^(\s+)?%s\s+(.*)(\()" %(CellName)
        for CellContent in content:
            if regexExtraction(regexRemoveCell, CellContent):
                removeModule.append(CellName.strip())
    # Logging.message("INFO",f"MODULE INSTANTIATED\n    {removeModule}")

    for i, con in enumerate(content):
        # Remove // From The Verilog Content
        content[i] = removeContentData(r"//(.*)(input|output)(.*)",content[i])
        content[i] = removeContentData(r"//.*",  content[i])
        # Remove /**/ From The Verilog Content
        content[i] = removeContentData(r"/\*(.|\n)*?\*/",  content[i])
        # Remove task From The Verilog Content
        content[i] = removeContentData(
            r"task(\s+)(.|\n)*?endtask.*", content[i])
        # Remove Function From The Verilog Content
        content[i] = removeContentData(
            r"function(\s+)(.|\n)*?endfunction.*",  content[i])
        # Remove `if|`eli
        content[i] = removeContentData(
            r"`if.*|`el.*|`en.*",  content[i])
        extractedContent = re.finditer(r"module(\s+)(.*)", moduleList[i], re.M)
        if extractedContent:
            for matchNum, match in enumerate(extractedContent, start=1):
                moduleName = match.group(2).strip()
        if moduleName.strip() not in removeModule:
            try:
                PortDataDic = portExtraction(
                    content[i], verFile, moduleName, PortDataDic)                
            except:
                Logging.message(
                    "WARNING", f"INVALID PORT MAY BE GIVEN IN VERILOG FILE\n    {verFile}")
    return PortDataDic

# Read Verilog file From PATH and Create JSON 
def vlogProcess(verFile):
    try:
        content = read(verFile)
        FileContent = content
        Logging.message(
            "INFO", f"READING THE VERILOG FILE AND EXTRACTING INFORMATION\n    {verFile}")
    except:
        Logging.message(
            "ERROR", f"COULDN'T READ THE VERILOG FILE\n    {verFile}")
    # Removing Beginning And Ending Space
    content = re.sub(r"^\s+|\s+$", "", content)
    # Will Split over semicolon
    content = content.replace(";", ";\n")
    # Removing Space From Beginning Of Eache Line
    content = re.sub(r"\n\s+", "\n", content)
    # Removing Space End Of Each Line
    content = re.sub(r"\s+\n", "\n", content)
    try:
        portData = jsonRead(".temp/vlog")
    except:
        portData = {}
    portData = vLogModule(content,  verFile, portData)
    return portData, FileContent

# Create VLOG JSON Dictionary and wirte into .temp folder
def vlogProcessMain(PATH,IP_TYPE):
    """
    This function will create and update the json data for each .lib file from
    given library path. Json data will be created and updated for given cell name only.
    Json data will be saved in <RUN_DIRECTORY>/.temp path.

    Usage::
        >>> import vlogProcess
        >>> vlogProcess.LibJsonMain("LIBRARY_PATH", "IP_TYPE")

    :param: PATH: library path for .lib files
    :param: IP_TYPE: Ip type for which json data will be created. ex. io,memory,logic etc.
    :returns: None
    """
    isFile = os.path.isfile(PATH)
    if not isFile: 
        ALL_VLOG = ""   
        vlogJsonContent = {}
        vlogFileContent = {}
        FileList = getFiles(PATH)
        if len(FileList) == 0:
            Logging.message("WARNING", f"COULDN'T FOUND VERILOG FILE INSIDE\n    {PATH}")

        for fileName in FileList:
            vlogDic, FileContent = vlogProcess(fileName)
            # For IO,LOGIC,AMS etc. Create JSON Dictionary with FileName
            if IP_TYPE.strip() != "MEMORY":
                vlogJsonContent[os.path.basename(fileName)] = vlogDic
                try:
                    prevDic = jsonRead(".temp/vlog")
                    vlogDicMerge = merge_dict(prevDic, vlogJsonContent)
                    jsonWrite(".temp/vlog", vlogDicMerge)
                except:
                    prevDic = {} 
                    vlogDicMerge = vlogJsonContent      
                    jsonWrite(".temp/vlog", vlogDicMerge)
             # For Memory Merge all vlog into ALL.v JSON dictionary        
            else:
                vlogJsonContent["ALL.v"] = vlogDic
                try:
                    prevDic = jsonRead(".temp/vlog")
                    vlogDicMerge = merge_dict(prevDic, vlogJsonContent)
                    jsonWrite(".temp/vlog", vlogDicMerge)
                except:
                    prevDic = {} 
                    vlogDicMerge = vlogJsonContent      
                    jsonWrite(".temp/vlog", vlogDicMerge)      

            # Create JSON Dictionary with filename for same view Comparison
            vlogFileContent[os.path.basename(fileName)] = vlogDic
            try:
                prevFileDic = jsonRead(".temp/vlogFile")
                vlogFileDicMerge = merge_dict(prevFileDic, vlogFileContent)
                jsonWrite(".temp/vlogFile", vlogFileDicMerge)
            except:
                prevFileDic = {} 
                vlogFileDicMerge = vlogFileContent      
                jsonWrite(".temp/vlogFile", vlogFileDicMerge) 

            # MERGE FILES INTO ALL.v
            if IP_TYPE.strip() == "MEMORY":
                ALL_VLOG = ALL_VLOG + f"# FILE : {os.path.basename(fileName)}\n" + FileContent + "\n\n"
        
        if ALL_VLOG.strip():
            # Logging.message("INFO", f"Writing file\n    {os.path.join(PATH,'ALL.v')}")
            with open(os.path.join(PATH,"ALL.v"), 'w') as f:
                f.write(ALL_VLOG)   
    else:
        Logging.message("ERROR", f"EXPECTED PATH BUT FOUND FILE\n    {PATH}")        

# Extract File names from Path
def getFiles(PATH):
    """
    This function will extract the file name and create a file list from given path.

    Usage::
        >>> import vlogProcess
        >>> vlogProcess.getFiles("LIBRARY_PATH")

    :param: PATH: library path from where file list will be created.
    :returns: file list as list
    
    """
    FileList = []
    for path, subdirs, files in os.walk(PATH): 
        for fileName in files:       
            FileList.append(os.path.join(path,fileName))
    return FileList

# Update and merge Previous dictionary
def merge_dict(prev_dic, new_dic):
    """
    This function will update and merge the previous json data with new json data.

    Usage::
        >>> import vlogProcess
        >>> vlogProcess.merge_dict("PREVIOUS_JSON_DATA", "NEW_JSON_DATA")

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



