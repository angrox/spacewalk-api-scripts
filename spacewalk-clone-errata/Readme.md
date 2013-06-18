spacewalk-compare-packages.py 
=============================

What is this script for? 
------------------------

This script clones errata (including the packages) from one channel to another channel
(just like the gui)


Usage
-----

<pre>
Usage: spacewalk-clone-errata.py [options]                                                                                                      
                                                                                                                                                
Options:                                                                                                                                        
  -h, --help            show this help message and exit                                                                                         
  -f CFG_FILE, --config-file=CFG_FILE                                                                                                           
                        Config file for servers, users, passwords. Defaults to                                                                  
                        '/etc/rhn/rhn-api-user.conf'                                                                                            
  -e ERRATA, --errata=ERRATA                                                                                                                    
                        A comma seperated list of errata ex:                                                                                    
                        "RHBA-2013:0909,RHBA-2013:0910"                                                                                         
  -c CHANNEL, --channel=CHANNEL                                                                                                                 
                        The channel label of the destination channel          
<pre>

The configuration file must be parseable bei ConfigParser:<br>
Example: 

<pre>
[Spacewalk]
spw_server = spacewalk.example.com
spw_user   = api_user_1
spw_pass   = api_password_1
</pre>
