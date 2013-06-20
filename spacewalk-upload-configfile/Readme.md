spacewalk-upload-configfile.py
=============================

What is this script for? 
------------------------

Pushes a file to a given Configuration Channel and issues an immidiate push to all
subscribed systems (optional)

Usage
-----

<pre>
Usage: spacewalk-upload-configfile.py [options]                                                                                                 
                                                                                                                                                
Options:                                                                                                                                        
  -h, --help            show this help message and exit                                                                                         
  -f CFG_FILE, --config-file=CFG_FILE                                                                                                           
                        Config file for servers, users, passwords. Defaults to                                                                  
                        '/etc/rhn/rhn-api-user.conf'                                                                                            
  -u UPLOAD, --upload-file=UPLOAD                                                                                                               
                        File which should be uploaded                                                                                           
  -c CHANNEL, --configchannel=CHANNEL                                                                                                           
                        Configuration channel in which the file should be                                                                       
                        pushed                                                                                                                  
  -p, --issuepush       Issue a push-to-all-subscribed-system to the                                                                            
                        configchannel after uploading the new file         
</pre>

The configuration file must be parseable bei ConfigParser:<br>
Example: 

<pre>
[Spacewalk]
spw_server = spacewalk.example.com
spw_user   = api_user_1
spw_pass   = api_password_1
</pre>
