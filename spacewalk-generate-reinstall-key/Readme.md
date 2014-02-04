spacewalk-generate-reinstall-key.py
===================================

What is this script for? 
------------------------

It generates a reinstall activation key for an already registered spacewalk client. 
This key is printed on STDOUT for further processing.


Usage
-----

<pre>
Usage: spacewalk-generate-reinstall-key.py [options]                                                                                                             
                                                                                                                                                                 
Options:                                                                                                                                                         
  -h, --help            show this help message and exit                                                                                                          
  -f CFG_FILE, --config-file=CFG_FILE                                                                                                                            
                        Config file for servers, users, passwords. Defaults to                                                                                   
                        '/etc/rhn/rhn-api-user.conf'                                                                                                             
  -s SERVERNAME, --servername=SERVERNAME                                                                                                                         
                        Hostname as seen in the Spacewalk/Satellite Server                                                                                       
  --deleteduplicated    Delete duplicated host entries                                                                                                           
  -d, --debug           print debug entries                      
<pre>

[Spacewalk]
spw_server = spacewalk.example.com
spw_user   = api_user_1
spw_pass   = api_password_1
</pre>
