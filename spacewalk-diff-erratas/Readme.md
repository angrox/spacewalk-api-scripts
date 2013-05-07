spacewalk-diff-erratas.py
===


This script checks if there is a newer version of a package for specific 
systems available.

<pre>
 usage: spacewalk-diff-erratas.py [options]

 options:
   -h, --help            show this help message and exit
   -f CFG_FILE, --config-file=CFG_FILE
                         Config file for servers, users, passwords
   -p PACKAGE, --package=PACKAGE
                         Package name, ex: bash
   -s SYSTEM, --system=SYSTEM
                         Name of the System or "all" for all systems. Regex can
                         be used to specify more than one server, ex.
                         webserver*
   -c CHANNEL, --channel=CHANNEL
                         [OPTIONAL] The channel to check against. By default
                         systems channels (base and child) are checked. If you
                         use this option only THIS channel is checked. No child
                         channels will be checked!
   -r RELEASE, --release=RELEASE
                         [OPTIONAL] Check only a specific release. Values are:
                         5, 6

</pre>
 

The configuration file must be parseable bei ConfigParser:
Example: 

<pre>
[Spacewalk]
spw_server = spacewalk.example.com
spw_user   = api_user_1
spw_pass   = api_password_1
</pre>

