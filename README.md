# json-to-kv

JsonFilter:
Convert json to key=value format, and filter the json fields.

The following python script will convert a folder with json files to a new 'filtered' folder with kv format (key1=value1 key2=value2...)

Usage: 
1. Edit settings.ini 
fields_file - Full fields file location. The fields file contains the desired fileds to keep from the json.
dir - Source folder with json files to filter and convert.
folders - Which inner folders inside the 'dir' folder to use. (Future: make this option optional, currently its mandatory)

2. Edit fields.txt
In fields.txt under [fields] stanza, write the desired fields from the jsons that will be converted into kv format.
Json hierarchy is expressed using "." seperator. 

Format: 
        JSON                                                                                fields.txt
        ------------------------------------------------------------------------------------------------------------------
       "field": "value"                             							            "newfield" => field=newfield
       "parent": { "field": "value" } 		      	    					            	"newfield" => parent.field=newfield
   		 "grand" : { "otherfield:": "othervalue", parent": { "field": "value"}}	"newfield" => grand.parent.field=newfield

Example:
[fields]
jsonparent.jsonchild=kvfield1
jsonparent2=kvfield2

3. Run manually or as schedule
Windows - 
Install python 2.7
Run jsonfilter.cmd

Linux  -
Run "python jsonfilter.py"
