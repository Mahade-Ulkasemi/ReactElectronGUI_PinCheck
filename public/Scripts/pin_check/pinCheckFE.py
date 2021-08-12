#!/tool/pandora64/.package/python-3.7.2/bin/python3
import sys, re
import os
import shutil
from argparse import ArgumentParser, RawTextHelpFormatter
from utils import read,makeDirs,remove_file,check_file
from log import Logging
from pinCheckMain import pinCheckMain
from timer import countdown

script_name = os.path.basename(__file__)  # script name
script_path = os.path.realpath(__file__)  # script abs path
script_dir, script_file = os.path.split(script_path)

# Get Script Inputs
def main_parser():
    """
    : This function get the arguments from the terminal & return it into a list as "args".
    : usage                   : main_parser().
    : parameter parser        : This holds a function of argparse.
    : parameter command_group : This holds the function for the feature of the mutually exclusive group.
    : prameter args           : This holds the command line into a dictionary & return it.
    """
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    group1 = parser
    group2 = parser
    group3 = parser
    
    group1.add_argument("-i", "--ip", required=True, nargs=1, metavar='<IP_TYPE>', action="store", dest="IP_TYPE",
                                help="GIVE IP TYPE FOR PIN CHECK FE")

    group2.add_argument("-l", "--library", required=True, nargs=1, metavar='<LIBRARY>', action="store", dest="LIBRARY",
                                help="GIVE LIBRARY PATH FOR PIN CHECK FE")

    args = vars(parser.parse_args())
    return args


def main(args):
    # Remove Temporary files and folders
    try:
        if check_file(".temp",False):
            shutil.rmtree(".temp")
        makeDirs('.temp')
        remove_file('process.log')
    except:
        Logging.message("ERROR", "DON'T HAVE PERMISSION TO REMOVE THE <.temp> <process.log>")
    
    # countdown(100)
    Logging.message("INFO",f"RUNNING THE <{script_name}> SCRIPT")

    if not check_file(args["LIBRARY"][0],False):
        Logging.message("ERROR",f"INVALID LIBRARY PATH OR PATH NOT EXIST\n    {args['LIBRARY'][0]}")
        
    # Create Library and Compare PIN 
    if args["IP_TYPE"] and args["LIBRARY"]:    
        ip_type = args["IP_TYPE"][0].upper()
        lib_path = args["LIBRARY"][0]
        file_extension = read(os.path.join(script_dir,"EXTENSION"))
        pinCheckMain(ip_type,lib_path,file_extension)

if __name__ == '__main__':
    args = main_parser()
    main(args)
    