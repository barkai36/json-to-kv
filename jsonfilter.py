import json
import sys
import os
import logging
import time
import ConfigParser
import random
import collections
import shutil


# Creating new filtered file with key=value paires, based on existing JSON files
# Using fields from 'fields' array


def parse_file(srcfile,dstfile,fields):

    try:
        jsonfile = open(srcfile)
    except:
        logger.error('Failed to load json file:'+srcfile)
        raise

    try:
        output = open(dstfile,'wb')
    except:
        logger.error('Unable to create new file:'+srcfile)
        raise

    for i, line in enumerate(jsonfile):
        try:
            input = json.loads(line)
        except:
            logger.error('Failed to load json row from file:'+srcfile+' . Line:'+str(i+1))

        data = collections.OrderedDict()
        for field in fields.keys():
            newfield = fields.get(field)
            try:
                if "#" in field: # Comment in fields file - ignore this field
                    pass
                elif "." in field:  # field is in other field
                    field1, field2 = field.split(".")
                    data[newfield] = input[field1][field2]
                else:               # field is not in other field
                    data[newfield] = input[field]
            except:
                logger.warn('EXCEPTION! could not read field '+field+' in line '+str(i+1))
                logger.warn(sys.exc_info()[0])

        # Write found keys to target file
        for key,value in data.items():
            #DEBUG
            #print str(i)+':'+str(key)+' = '+unicode(value)
            #END OF DEBUG
            output.write('%s="%s" ' % (key,unicode(value).encode('utf8')))
        output.write('\r\n') #End of JSON, end of line



    logger.info('Finished parsing file:'+str(srcfile)+' . Total lines:'+str(i))
    jsonfile.close()
    output.close()


def read_ini(settings_file,conf_name):
    try:
        config = ConfigParser.RawConfigParser()
        config.read(settings_file)
        value =  config.get('Conf',conf_name)
        return fix_folder_path(value)
    except:
        logger.error("unable to extract \""+conf_name+"\" from ini file")
        logger.error(sys.exc_info())
        raise


def read_fields(fields_file,stanza):
    try:
        logger.info('Reading fields file from:'+fields_file)

        fieldsconfig = ConfigParser.RawConfigParser()
        fieldsconfig.optionxform=str # Disable auto lower case for config file, user Upper/Lower case as original file.
        fieldsconfig.read(fields_file)
        fields=collections.OrderedDict(fieldsconfig.items(stanza))

        return fields
    except:
        logger.error('EXCEPTION! could not read fields file')
        logger.error('Location:'+fields_file)
        logger.error(sys.exc_info())
        raise

# Add \\ instead of each \ in the path, except UNC paths that starting with \\
def fix_folder_path(path):
    unc = False
    if path[:2] == '\\\\': # Look for UNC path, trim the starting '\\' before running the replace
        unc = True
        path=path[2:] # Trim the '\\' before replacing the single '\'
    path = str(path).replace('\\','\\\\')
    if unc == True:     # Bring back the starting '\\' in the UNC path
        path = '\\\\'+path
    return path


def parse_folder(dir,folders,fields):
    start_time = time.time() # Filtering starting time
    filecnt=0       # File counter
    filefiltercnt=0 # Filtered files counter
    fileserrorcnt=0 # Errored files counter

    logger.info('Starting parsing json files')

    for root, subFolders, files in os.walk(dir):
        for file in files:  #Scan all the files in the directory
            for folder in folders: # Search for each desired folder in INI file
                if root.find('Communications') != -1 and root.find(folder) != -1 and root.find('-filter') == -1:
                    # Only non-filtered files, from INI folders, from 'Communications' folder
                    filecnt+=1
                    currjson = os.path.join(root,file)  # Set current JSON file to parse
                    currjson = os.path.abspath(currjson) #Support long pathnames
                    newdir=root+'-filter'               # Set new dir for filtered file
                    newjson=os.path.join(newdir,file)   # Set new full path for filtered file
                    newjson=os.path.abspath(newjson) #Support long pathnames
                    if os.path.isfile(newjson):         # Do nothing if filtered file already exists
                        pass
                    else:                               # Filter the JSON file
                        if os.path.isdir(newdir):       # Check if new dir already exists, otherwise create it
                            pass
                        else:
                            logger.info("creating dir:"+newdir)
                            os.makedirs(newdir)
                        logger.info('Parsing file #'+str(filefiltercnt)+': '+currjson)
                        logger.info('New file: '+newjson)
                        try:
                            parse_file(currjson,newjson,fields) # Parse the chosen JSON file
                            filefiltercnt+=1
                        except:
                            pass
                            fileserrorcnt+=1

    logger.info('Found '+str(filecnt)+' files. Filtered '+str(filefiltercnt)+' files. Skipped '+str(filecnt-filefiltercnt-fileserrorcnt)+' files. Errored '+str(fileserrorcnt)+' files')
    logger.info('Finished parsing json files')
    logger.info('Total run time: '+str(round(time.time() - start_time,2))+' seconds')


def clean_old_dirs(dir, folders):
    skipped=0
    removed=0
    for root, subFolders, files in os.walk(dir):
        for folder in folders: # Search for FILTERED folders desired folder in INI file, delete if older than 1 week
                if root.find('Communications') != -1 and root.find(folder) != -1 and root.find('-filter') != -1:
                    orig_dir=root[:-7]
                    print 'root: '+root
                    print 'orig_dir:'+orig_dir
                    # Check if original directory still exists, delete if not
                    if os.path.isdir(orig_dir):
                        print 'Orig dir for: '+root+' already exists!'
                        print 'Orig dir: '+orig_dir
                        skipped+=1
                    else:
                        logger.info('Removing old dir:'+root)
                        shutil.rmtree(root) # Remove the found folder, which is older than one week
                        removed+=1
    logger.info('Removed '+str(removed)+' folders, skipped '+str(skipped)+' folders.')

def main():
    try:
        settings_file = 'settings.ini'  # INI file name
        fields_file= read_ini(settings_file,'fields_file') # File location with desired fields to extract
        dir = read_ini(settings_file,'dir') # Location of dir with  JSON files
        folders = read_ini(settings_file,'folders').split(',') # Folders to find in the dir. Only files in these folders will be extracted
        fields = read_fields(fields_file,'fields')      # Read regular fields
        parse_folder(dir,folders,fields)
        clean_old_dirs(dir,folders)


    except:
        logger.error(sys.exc_info())
        pass

def set_logger():
    main_dir = os.getcwd() # current dir for log file
    date = time.strftime("%d-%m-%Y") # current day for log file name
    pid = str(random.randrange(0000, 9999, 4))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create a file handler
    #handler = logging.FileHandler('C:\Jsonfilter\jsonfilterlog.log')
    handler = logging.FileHandler(os.path.join(main_dir,date+'-jsonfilterlog.log'))
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - '+pid+' - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    return logger


if __name__ == "__main__":
    logger = set_logger()
    logger.info('------STARTING----------')
    main()
    logger.info('------FINISHED----------\n')

