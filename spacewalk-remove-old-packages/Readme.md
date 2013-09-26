spacewalk-remove-old-packages.py
===============================

What is this script for? 
------------------------

 This script deletes all old packages from one channel or deletes packages
 without channel. 

 To remove the packages from the filesystem you must use spacewalk-data-fsck
 afterwards (-r option).

 BE CAREFUL WITH THIS SCRIPT! TEST IT BEFORE USING IT IN PRODUCTION!
 I must point again at the "WITHOUT ANY WARRANTY" line :-)


Usage
-----

<pre>
 usage: spacewalk-remove-old-packages.py [options]
 
 options:
   -h, --help            show this help message and exit
   -s SPW_SERVER, --spw-server=SPW_SERVER
                         Spacewalk Server
   -u SPW_USER, --spw-user=SPW_USER
                         Spacewalk User
   -p SPW_PASS, --spw-pass=SPW_PASS
                         Spacewalk Password
   -f CFG_FILE, --config-file=CFG_FILE
                         Config file for servers, users, passwords
   -c CHANNEL, --channel=CHANNEL
                         Channel Label: ie."myown-rhel-6-x86_64"
   -w, --without-channels
                         Delete packages without channel. Overwrites the
                         channel option
   -n, --dryrun          No Change is actually made, only print what would be
                         done
</pre>

The configuration file must be parseable bei ConfigParser:<br>
Example: 

<pre>
[Spacewalk]
spw_server = spacewalk.example.com
spw_user   = api_user_1
spw_pass   = api_password_1
</pre>
