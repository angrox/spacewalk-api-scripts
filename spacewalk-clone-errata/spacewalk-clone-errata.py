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
# Clones one or more errata to a specific channel. just like in the gui :-) 
#

import xmlrpclib
import ConfigParser
import optparse
import sys
import os
import re

from optparse import OptionParser
from distutils.version import LooseVersion



def parse_args():
    parser = OptionParser()
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords. Defaults to '/etc/rhn/rhn-api-user.conf'")
    parser.add_option("-e", "--errata", type="string", dest="errata",
            help="A comma seperated list of errata ex: \"RHBA-2013:0909,RHBA-2013:0910\"")
    parser.add_option("-c", "--channel", type="string", dest="channel",
            help="The channel label of the destination channel")
    
    #
    # Put other options here
    #

    (options,args) = parser.parse_args()
    return options






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

    if options.errata is None: 
        print "Please specify an errata (see -h for help)"
        sys.exit(1)
    if options.channel is None: 
        print "Please specify a valid channel (see -h for help)"
        sys.exit(1)


    # Log in
    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % spw_server, verbose=0)
    spacekey = spacewalk.auth.login(spw_user,spw_pass)

    
    
    #
    # Process the data or whatever needs to be done go here
    #

    allerrata=options.errata.replace(" ", "").split(",")

    # Check if errata exists
    for erratum in allerrata:
        try: 
            errata_details=spacewalk.errata.getDetails(spacekey, erratum)
        except xmlrpclib.Fault, err:
            print "Error getting errata details (Code %s, %s)" % (err.faultCode, err.faultString)
            spacewalk.auth.logout(spacekey)
            sys.exit(1)
    
    
    # Check if channel exists
    try: 
        channel_details=spacewalk.channel.software.getDetails(spacekey, options.channel)
    except xmlrpclib.Fault, err:
        print "Error getting channel details (Code %s, %s)" % (err.faultCode, err.faultString)
        spacewalk.auth.logout(spacekey)
        sys.exit(1)

    # Check if errata is already in channel
    channel_erratas=spacewalk.channel.software.listErrata(spacekey, options.channel)
    for cherrata in channel_erratas:
        for erratum in allerrata:
            if options.errata in cherrata['advisory_name']:
                print "Erratum %s is already in channel %s" % (erratum, options.channel)
                spacewalk.auth.logout(spacekey)
                sys.exit(1)
            # Check unique id:
            if re.match(".*-%s" % erratum.split("-")[1], cherrata['advisory_name']) is not None: 
                print "Erratum %s is already in channel %s as ID %s" % (erratum, options.channel, cherrata['advisory_name'])
                spacewalk.auth.logout(spacekey)
                sys.exit(1)

    # Clone errata
    print "Cloning errata: %s" % allerrata
    spacewalk.errata.clone(spacekey, options.channel, allerrata)
    

    # logout
    spacewalk.auth.logout(spacekey)


## MAIN
if __name__ == "__main__":
    main()  

