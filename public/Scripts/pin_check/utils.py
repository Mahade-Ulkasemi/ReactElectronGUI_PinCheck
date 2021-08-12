from log import Logging
import os, re
import json
import openpyxl
from collections import OrderedDict


def added_write(filename, content):
    '''
    This Function will append/add a new text to the already existing file or a new file.
       
    Usage:: 
        >>> import utils.py
        >>> utils.added_write("filename", "content")

    :param: filename: existing or new file name 
    :param: content: text or string which needs to append/add  to the existing file or a new file.

    :returns: None
    '''
    with open(filename, 'a') as f:
        f.write(content)

def regexExtraction(regex, content):
    """
    This function will extract information from a given regular expression. It will search the regular expression pattern in the given string.

    Usage:: 
        >>> import utils.py
        >>> utils.regexExtraction("regex", "content")

    :param: regex: regular expression.
    :param: content: text or string where regular expression will be searched.

    :returns: all match content as list.
    """
    updatedContent = []
    extractedContent = re.finditer(regex, content, re.MULTILINE)
    if extractedContent:
        for matchNum, match in enumerate(extractedContent, start=1):
            updatedContent.append(match.group())
    return updatedContent

def check_file(filename, flag=False):
    """
    This function will check whether the specified path exists or not.

    Usage:: 
        >>> import utils.py
        >>> utils.check_file("filename", "flag")

    :param: filename: file name or path you want to check.
    :param: flag: True show a warning massage. False don't show warning massage if file or path not found. (default=False)

    :returns: Ture if file or path exist, False if file or path not exist.
    """
    if os.path.exists(filename):
        return True
    else:
        if flag:
            Logging.message('WARINIG', 'FILE NOT FOUND: %s' % filename)
        return False


def excelRead(file):
    """
    This function will use openpyxl load_workbook( ) function to access an MS Excel file in openpyxl module.\n
    You have to keep in mind that load workbook function only works if you have an already created file on your disk and you want to open workbook for some operation.

    Usage:: 
        >>> import utils.py
        >>> utils.excelRead("file")

    :param: file: excel file name or path you want to access.

    :returns: Excel workbook to read or write or add or delete sheets, or cells or any other thing you want to do.
    """
    try:
        Logging.message("INFO", f"READING THE <{file}> FILE")
        wb = openpyxl.load_workbook(file, data_only=True)
        return wb
    except:
        Logging.message(
            "ERROR", f"INVALID <.xlsx> FORMAT OR <{file}> FILE NOT FOUND")

def added_jsonWrite(file, dictionary):  
    """
    This function will open a already existing file or a new file and parse JSON string.\n
    It will use "update()" method to add the 'dictionary' if the key is not in the parse JSON dictionary. If the key is in the dictionary, it updates the key with the new value.\n
    Finally It will use json.dump() method to write updated dictionary as JSON formatted data into given file.

    Usage:: 
        >>> import utils.py
        >>> utils.added_jsonWrite("file", "dictionary")

    :param: file: file name or path.
    :param: dictionary: dictionary you want to add or update with new value.

    :returns: None.
    """
    with open(file, "r+") as file:
        data = json.load(file)
        data.update(dictionary)
        file.seek(0)
        file.truncate()
        json.dump(data, file)

def jsonWrite(file, content):
    """
    This function will open a already existing file or a new file and It will use json.dump() method to write given dictionary as JSON formatted data into given file.

    Usage:: 
        >>> import utils.py
        >>> utils.jsonWrite("file", "content")

    :param: file: file name or path.
    :param: content: dictionary you want to add or write as JSON format.

    :returns: None.
    """ 
    with open(f"{file}.json", 'w') as f:
        json.dump(content, f, ensure_ascii=False)

def jsonRead(file):
    """
    This function will open a already existing file to parse and return JSON string.\n

    Usage:: 
        >>> import utils.py
        >>> utils.jsonRead("file")

    :param: filen: file name or path.

    :returns: JSON string.
    """ 
    with open(f"{file}.json", 'r') as f:
        return json.load(f, object_pairs_hook=OrderedDict)

def write(filename, content, Flag=True):
    '''
    This Function will add a new text to the already existing file or a new file.
       
    Usage:: 
        >>> import utils.py
        >>> utils.write("filename", "content", "Flag")

    :param: filename: existing or new file name 
    :param: content: text or string which needs to add to the existing file or a new file.
    :param: Flag: True show a massage. False don't show massage while writting file. (default=True)

    :returns: None
    '''
    if Flag:
        Logging.message("INFO", f"Writing <{filename}> file")
    with open(filename, 'w') as f:
        f.write(content)


def read(filename):
    '''
    This Function will read the content of the existing file and return as string.
       
    Usage:: 
        >>> import utils.py
        >>> utils.read("filename")

    :param: filename: existing file name 
    
    :returns: file content as string
    '''
    with open(filename, 'r') as f:
        content = f.read()
    return content

def remove_file(filename):
    '''
    This Function will remove the given file name or path using os.remove() method.

    Usage:: 
        >>> import utils.py
        >>> utils.remove_file("filename")

    :param: filename: file name or path you want to remove.
    
    :returns: None
    '''
    if check_file(filename,flag=False):
        os.remove(filename)


def makeDirs(dir):
    '''
    This Function will create a directory recursively using os.makedirs() method.

    Usage:: 
        >>> import utils.py
        >>> utils.makeDirs("dir")

    :param: dir: directory name or path you want to make.
    
    :returns: None
    '''
    if not check_file(dir,flag=False):
        os.makedirs(dir)