spacewalk-rhn-sync
==================

Script that syncs RPM packages from the Red Hat Network to a local
Spacewalk Server

Author: Martin Zehetmayer <angrox@idle.at>

This script uses code and the same configuration file from the 
rhn-clone-errata.py script from Andy Speagle <andy.speagle@wichita.edu>
which can be found in the official spacewalk git repostiory
The script depends on the mrepo package from Dag Wiers which can be found
on http://dag.wieers.com/home-made/mrepo/

THANKS both of you for your great work! 



REQUIREMENTS
You need the following requirements to use spacewalk-rhn-sync.py: 

- An installed and configured Spacewalk server
- A valid RHN subscription (username/password)
- The script was tested on a RHEL6/Centos6 machine (python 2.6.6) 
- mrepo 0.8.8 installed (for RHEL5/6)

CONFIGURATION
Have a look at the example configuration file which comes with the script. 
Note that the config file is identical with the configuration file 
used by rhn-clone-errata.py which can be found in the official spacewalk 
repository. Only the [Global] section with the proxy configuration is 
new to spacewalk-rhn-sync.py

In order to sync the packages the script utilize the rhnget script which
comes with the mrepo package from Dag Wiers. We do not use the complete
mrepo sync feature so we just need to generate a system id and register 
it on the Red Hat network. 

Quote from the mrepo documentation: 
RHN systemid creation
For each distribution you want to add to mrepo, you need to have a valid
RHN systemid. You can create a systemid (provided you have the correct
entitlements to do so) by using the gensystemid tool that comes with
mrepo, eg.

gensystemid -r 6Server -a x86_64 /var/mrepo/rhel6s-x86_64

The tool will create a new system called _<hostname>-6Server-x86_64-mrepo_,
register this system on RHN and create a systemid file in
_/var/mrepo/rhel6s-x86_64_



You can copy the systemid to a location suiteable for you, for example /etc/rhn/.

In addition a /etc/sysconfig/rhn/up2date-uuid file needs to be generated:

# UUID=$(uuidgen) ; /bin/echo -e "uuid[comment]=Universally Unique ID for this server\nrhnuuid=$UUID" > /etc/sysconfig/rhn/up2date-uuid

Note that you need to generate a own systemid file for each distribution! 


USAGE
example: 
spacewalk-rhn-sync.py -f /etc/rhn/rhn-clone-errata.conf -c rhel-x86_64-server-6 -b 2012-05-20 -g /etc/rhn/systemid_rhel6
 - clones the errata from the rhel6 x86_64 channel to the spacewalk server and local
   channel configured in /etc/rhn/rhn-clone-errata.conf
