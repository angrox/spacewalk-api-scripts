#!/usr/bin/python
#
# This script is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ---------------
#
# This script generates a new reinstall activation key for a existing
# machine. 
#

import xmlrpclib
import ConfigParser
import optparse
import sys
import os
import re

from optparse import OptionParser
from distutils.version import LooseVersion

options=0



def parse_args():
    global options
    parser = OptionParser()
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords. Defaults to '/etc/rhn/rhn-api-user.conf'")
    parser.add_option("-s", "--servername", type="string", dest="servername",
            help="Hostname as seen in the Spacewalk/Satellite Server")
    parser.add_option("--deleteduplicated", action="store_true", dest="deleteduplicated", default=False,
            help="Delete duplicated host entries")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,
            help="print debug entries")
    
    (options,args) = parser.parse_args()
    return options



def debug(txt):
    if options.debug == True:
        print txt


def main():         
    # Get the options
    options = parse_args()
    # read the config
    if options.cfg_file is None:
        options.cfg_file="/etc/rhn/rhn-api-user.conf"
    config = ConfigParser.ConfigParser()
    try:
        config.read (options.cfg_file) 
    except:
        print "Could not read config file %s.  Try -h for help" % options.cfg_file
        sys.exit(1)
    try: 
        spw_server = config.get ('Spacewalk', 'spw_server')
        spw_user = config.get ('Spacewalk', 'spw_user')
        spw_pass = config.get ('Spacewalk', 'spw_pass')
    except: 
        print "The file %s seems not to be a valid config file." % options.cfg_file
        sys.exit(1)

    #
    # Check here if options are present
    #
    if options.servername is None: 
        print "Missing hostname."
        sys.exit(1)

    # Log in
    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % spw_server, verbose=0)
    spacekey = spacewalk.auth.login(spw_user,spw_pass)

    
    foundsystems = spacewalk.system.search.hostname(spacekey, options.servername)

    if len(foundsystems) == 0:
        debug("No systems found.")
        sys.exit(1)
   
    latestsystem=foundsystems[0]
    if len(foundsystems) > 1 and options.deleteduplicated == True:
        print "Deleting duplicated systems:"
        for dupsys in foundsystems[1:]:
            if spacewalk.system.deleteSystem(spacekey, dupsys['id']):
                debug(" - System %s / %s deleted" % (dupsys['hostname'], dupsys['id']))
            else:
                debug(" - Error deleting system %s / %s"  % (dupsys['hostname'], dupsys['id']))
            

    oldactivationkeys=spacewalk.system.listActivationKeys(spacekey, latestsystem['id'])
    reactivationkey=spacewalk.system.obtainReactivationKey(spacekey, latestsystem['id'])
    if reactivationkey is not None: 
        rettxt="%s:%s:%s:" % (reactivationkey,latestsystem['id'],latestsystem['hostname'])
        for oldact in oldactivationkeys:
            rettxt = "%s%s," % (rettxt,oldact)
        print rettxt[:-1]
        sys.exit(0)
    else:
        sys.exit(1)
    
    # logout
    spacewalk.auth.logout(spacekey)


## MAIN
if __name__ == "__main__":
    main()  

