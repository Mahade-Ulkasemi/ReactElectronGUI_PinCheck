import sys
import os, subprocess
from collections import OrderedDict, defaultdict
from utils import read, regexExtraction, makeDirs, check_file, write, remove_file, added_jsonWrite, jsonRead, jsonWrite
from log import Logging
import pathlib
import re
import json
import shutil
import openpyxl
from openpyxl import Workbook
from lef2json import LefJsonMain
from lib2json import LibJsonMain
from vlogProcess import vlogProcess, vlogProcessMain
from pinCompare import PinCompareMain

# Create Library For Pin Comparison
def create_library_setup(path):
    """
    This function will create the library setup path

    Usage::
        >>> import pinCheckMain
        >>> pinCheckMain.create_library_setup("LIBRARY_PATH")

    :param: path: library setup path 
    :returns: None
    """
    makeDirs(path)
    makeDirs(os.path.join(path, 'engr', 'lef'))
    makeDirs(os.path.join(path, 'engr', 'lib'))
    makeDirs(os.path.join(path, 'engr', 'verilog'))

# Check Valid LEF,LIB and VERILOG, Create Soft Link into Library Path
def fileCheck(fileName, lib_setup_path):
    """
    this function will create a soft link of the all lef,lib and verilog files into the library path.

    Usage::
        >>> import pinCheckMain
        >>> pinCheckMain.fileCheck("FILE_NAME","LIBRARY_PATH")

    :param: fileName: file path 
    :param: lib_setup_path: library path where file will be copied 
    :returns: "LEF": return LEF string if the file is lef. 
    :returns: "LIB": return LIB string if the file is lib. 
    :returns: "VERILOG": return VERILOG string if the file is verilog. 
    :return: fileName: if the file is lef, lib or verilog then the filename will be returned
    :return None,None for other file type

    """    
    global LEF
    global LIB
    global VERILOG

    if os.access(fileName, os.R_OK):
        content = read(fileName)
    else :
        Logging.message("ERROR", f"DON'T HAVE PERMISSION TO READ FILE\n    {fileName}")   
        content = None

    if content:      
        regexLef = r"^(\s+)?\bMACRO\b\s+(.*)"
        regexLib = r"^(\s+)?\bcell\b(\s+)?(\((.*)\)(\s+)?\{)"  
        regexVeilog = r"^(\s+)?\bmodule\b(\s+)?(.*)(\s+)?\("        
        head_tail = os.path.split(fileName)
        # LEF FILE CHECK
        if regexExtraction(regexLef, content):
            if not check_file(os.path.join(lib_setup_path,"engr","lef", head_tail[1])):
                # os.system("ln -s %s %s/engr/lef" % (fileName, lib_setup_path))
                shutil.copy(fileName, "%s/engr/lef" %lib_setup_path)
            LEF.append(head_tail[1])
            return "LEF", fileName
        # LIB FILE CHECK
        elif regexExtraction(regexLib, content):
            if not check_file(os.path.join(lib_setup_path, "engr","lib", head_tail[1])):
                # os.system("ln -s %s %s/engr/lib" % (fileName, lib_setup_path))
                shutil.copy(fileName, "%s/engr/lib" %lib_setup_path)
            LIB.append(head_tail[1])
            return "LIB", fileName
        # VERILOG FILE CHECK
        elif regexExtraction(regexVeilog, content):
            if not check_file(os.path.join(lib_setup_path, "engr", "verilog", head_tail[1])):
                # os.system("ln -s %s %s/engr/verilog" %(fileName, lib_setup_path))
                shutil.copy(fileName, "%s/engr/verilog" %lib_setup_path)
            VERILOG.append(head_tail[1])
            return "VERILOG", fileName
        else :
            return None, None
    else :
        return None, None

# Summarize Total Found FILES
def FileFoundSummary():
    """
    This function will show the all found lef files.
    """
    if not len(LEF) == 0:
        Logging.message(
                "INFO", "FOUND LEF FILE TOTAL :: %s" %len(LEF))
        for FILE in LEF:
            Logging.message("EXTRA", "%s" % FILE)
    if not len(LIB) == 0:
        Logging.message("INFO", "FOUND LIB FILE TOTAL :: %s" %len(LIB))
        for FILE in LIB:
            Logging.message("EXTRA", "%s" % FILE)
    if not len(VERILOG) == 0:
        Logging.message("INFO", "FOUND VERILOG FILE TOTAL :: %s" %len(VERILOG))
        for FILE in VERILOG:
            Logging.message("EXTRA", "%s" % FILE)

# Create RegEx content for lef, lib and verilog Extension
def get_ext_regex(extensions):
    """
    This function will create a regular expression to find the lef,lib and verilog file.

    Usage::
        >>> import pinCheckMain
        >>> pinCheckMain.get_ext_regex("EXTENSION")

    :param: extensions: extension data from EXTENSION file
    :returns: regex_ext: regular expression for file check. 
    """    
    regex_ext = ""
    ext_name = ""
    if extensions.group(5).strip():
        split_newline = extensions.group(5).strip().split("\n")
        for name_newline in split_newline:
            if name_newline.strip():
                ext_split = name_newline.strip().split(",")
                for num,ext in enumerate(ext_split,start=1):
                    if ext.strip():
                        ext = ext.split(".")
                        if len(ext) == 2:
                            ext = ext[1].strip()
                            ext = ext.split("*")
                            if len(ext) > 1:
                                for ext_num,name in enumerate(ext, start=0):
                                    if name.strip():
                                        ext_name = ext_name + ext[ext_num].strip() + ".*"
                            else:
                                ext_name = ext[0].strip()
                        else:
                            ext = ext[0].strip()
                            ext = ext.split("*")
                            if len(ext) > 1:
                                for ext_num,name in enumerate(ext, start=0):
                                    if name.strip():
                                        ext_name = ext_name + ext[ext_num].strip() + ".*"
                            else:
                                ext_name = ext[0].strip()
                                            
                        regex_ext = regex_ext + ext_name + "$|"
                        
                        ext_name = ""
    return regex_ext[:-1]

# Create RegEx to grep lef, lib and verilog files
def EXTENSION(file_extension):
    """
    This function will create the regular expression to find the lef,lib and verilog file from library path.

    Usage::
        >>> import pinCheckMain
        >>> pinCheckMain.EXTENSION("EXTENSION_FILE_DATA")

    :param: file_extension: extension file data from EXTENSION file
    :returns: VLOG_EXT_REGEX: regular expression for verilog file check. 
    :returns: LIB_EXT_REGEX: regular expression for lib file check.
    :returns: LEF_EXT_REGEX: regular expression for lef file check.
    """
    vlog_extensions = re.search(r"^(\s+)?(\b(VERILOG|verilog)\b)(.*)(?<={)((.|\n)*?(?=^(\s+)?}))",file_extension, re.MULTILINE)
    lib_extensions = re.search(r"^(\s+)?(\b(LIB|lib)\b)(.*)(?<={)((.|\n)*?(?=^(\s+)?}))",file_extension, re.MULTILINE)
    lef_extensions = re.search(r"^(\s+)?(\b(LEF|lef)\b)(.*)(?<={)((.|\n)*?(?=^(\s+)?}))",file_extension, re.MULTILINE)

    if vlog_extensions:
        vlog_ext_regex = get_ext_regex(vlog_extensions)
        if vlog_ext_regex.strip():
            VLOG_EXT_REGEX = r".*\.(%s)"%vlog_ext_regex.strip()
        else:
            VLOG_EXT_REGEX = None
            Logging.message("WARNING", "VERILOG EXTENSION NOT FOUND INSIDE EXTENSION FILE")
    else:
        Logging.message("WARNING", "VERILOG EXTENSION NOT FOUND INSIDE EXTENSION FILE")
        VLOG_EXT_REGEX = None
        
    if lib_extensions:
        lib_ext_regex = get_ext_regex(lib_extensions)
        if lib_ext_regex.strip():
            LIB_EXT_REGEX =r".*\.(%s)"%lib_ext_regex.strip()
        else:
            LIB_EXT_REGEX = None
            Logging.message("WARNING", "LIB EXTENSION NOT FOUND INSIDE EXTENSION FILE")
    else:
        Logging.message("WARNING", "LIB EXTENSION NOT FOUND INSIDE EXTENSION FILE")
        LIB_EXT_REGEX = None

    if lef_extensions:
        lef_ext_regex = get_ext_regex(lef_extensions)
        if lef_ext_regex.strip():
            LEF_EXT_REGEX = r".*\.(%s)"%lef_ext_regex.strip()
        else:
            LEF_EXT_REGEX = None
            Logging.message("WARNING", "LEF EXTENSION NOT FOUND INSIDE EXTENSION FILE")
    else:
        Logging.message("WARNING", "LEF EXTENSION NOT FOUND INSIDE EXTENSION FILE")
        LEF_EXT_REGEX = None

    return VLOG_EXT_REGEX, LIB_EXT_REGEX, LEF_EXT_REGEX

# Check File Extension
def check_extention_type(path, file_name, lib_setup_path, VLOG_EXT_REGEX, LIB_EXT_REGEX, LEF_EXT_REGEX):
    """
    This function will check the file extension.

    Usage::
        >>> import pinCheckMain
        >>> pinCheckMain.check_extention_type("LIBRARY_PATH","FILE_NAME","LIBRARY_SETUP_PATH","VLOG_EXT_REGEX", "LIB_EXT_REGEX", "LEF_EXT_REGEX")

    :param: path: library path from where file will be checked
    :param: file_name: file name 
    :param: lib_setup_path: library setup path where file will be copied.
    :param: VLOG_EXT_REGEX: regular expression for verilog file.
    :param: LIB_EXT_REGEX: regular expression for lib file.
    :param: LEF_EXT_REGEX: regular expression for lef file.
    :returns:  get_filetype: file type if the file is a lef,lib or verilog file.
    """
    VLOG_EXT = re.search(r"%s"%VLOG_EXT_REGEX, file_name.strip(), re.MULTILINE)
    LIB_EXT = re.search(r"%s"%LIB_EXT_REGEX,file_name.strip(), re.MULTILINE)
    LEF_EXT = re.search(r"%s"%LEF_EXT_REGEX,file_name.strip(), re.MULTILINE)
    if VLOG_EXT or LIB_EXT or LEF_EXT:
        get_filetype, get_file = fileCheck(os.path.join(path, file_name), lib_setup_path)
        if get_file:
            return get_filetype

# Grep LEF,LIB and VERILOG Files from Input Library path
def FindFiles(lib_setup_path,libpath,file_extension):
    """
    This function will search for the lef,lib and verilog file in the library path given as script input.

    Usage::
        >>> import pinCheckMain
        >>> pinCheckMain.FindFiles("LIBRARY_SETUP_PATH","LIBRARY_PATH","EXTENSION_DATA")

    :param: lib_setup_path: library setup path where file will be copied.
    :param: libpath: library path given as script input
    :param: file_extension: EXTENSION file data as string
    :returns:  FE_files: found file path as dictionary
    :returns: FileList: found file path as list
    """
    Logging.message("INFO", "SEARCHING FOR FILES IN LIBRARY PATH")
    Logging.message("EXTRA", "%s" % (libpath))
    FE_files = {
        'LEF': [],
        'LIB': [],
        'VERILOG': []
    }
    FileList = []
    VLOG_EXT_REGEX, LIB_EXT_REGEX, LEF_EXT_REGEX = EXTENSION(file_extension)
    for path, subdirs, files in os.walk(libpath):
        for file_name in files:
            file_type = check_extention_type(path, file_name, lib_setup_path,VLOG_EXT_REGEX, LIB_EXT_REGEX, LEF_EXT_REGEX)
            if file_type:
                FileList.append(os.path.join(path, file_name))
                FE_files[file_type].append(os.path.join(path, file_name))           
    return FE_files, FileList

# Create Library, Link Files and Compare pin between views
def libSetupRun(lib_setup_path,libpath,ip_type,file_extension):
    global LEF
    global LIB
    global VERILOG
    LEF = []
    LIB = []
    VERILOG = []
    create_library_setup(lib_setup_path)
    libpath = os.path.abspath(libpath)
    FE_files, FileList = FindFiles(lib_setup_path,libpath,file_extension)
    FileFoundSummary()
    Logging.message("INFO", "ALL FILES COPIED TO THE DIRECTORY\n    %s" %(lib_setup_path))
    cell_pin_compare(lib_setup_path,ip_type)

# Compare PIN between Views
def cell_pin_compare(lib_setup_path,ip_type):
    lefpath = os.path.join(lib_setup_path,"engr","lef")
    libpath = os.path.join(lib_setup_path,"engr","lib")
    vlogpath = os.path.join(lib_setup_path,"engr","verilog")  
    LefJsonMain(lefpath,ip_type)
    LibJsonMain(libpath,ip_type)
    vlogProcessMain(vlogpath,ip_type)
    wb = PinCompareMain(".temp/lef",".temp/lib",".temp/vlog",ip_type, ".temp/lefFile",".temp/libFile",".temp/vlogFile")
    makeDirs(os.path.join(lib_setup_path,"report"))
    wb.save(os.path.join(lib_setup_path,"report","pin_check.xlsx"))
    Logging.message("INFO", "PIN COMPARISON FINISHED...")
    
    
def pinCheckMain(IP_TYPE,LIB_PATH,file_extension):
    libpath =  os.path.abspath(LIB_PATH)
    lib_setup_path = os.path.abspath("FE_CHECK")    
    # Check Previous folder Exist or Not
    if check_file(lib_setup_path):
        Logging.message("WARNING","LIBRARY SETUP FILES ALREADY EXISTS. MANUALLY DELETE THE DIRECTORY")
        Logging.message("EXTRA", lib_setup_path)
        sys.exit()
    # Logging.message("INFO", "CREATING DIRECTORY OF LIBRARY SETUP FOR PIN CHECK FE")
    libSetupRun(lib_setup_path,libpath,IP_TYPE,file_extension)