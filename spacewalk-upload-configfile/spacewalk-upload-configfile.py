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
# Pushes a file to a configuration channel in Satellite/Spacewalk
#

import xmlrpclib
import ConfigParser
import optparse
import sys
import os
import re
import urllib2

from optparse import OptionParser
from distutils.version import LooseVersion



def parse_args():
    parser = OptionParser()
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords. Defaults to '/etc/rhn/rhn-api-user.conf'")
    parser.add_option("-u", "--upload-file", type="string", dest="upload",
            help="File which should be uploaded")
    parser.add_option("-c", "--configchannel", type="string", dest="channel",
            help="Configuration channel in which the file should be pushed")
    parser.add_option("-p", "--issuepush", action="store_true", dest="push",
            help="Issue a push-to-all-subscribed-system to the configchannel after uploading the new file")
    
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

    if options.upload is None or options.channel is None: 
        print "You need to specify a configchannel AND a file to upload."
        sys.exit(1)

    if not os.path.isfile(options.upload):
        print "File %s cannot be found." % options.upload
        sys.exit(1)

    try:
        f=open(options.upload, "r")
        filecontent=f.read()
        f.close
    except:
        print "Could not read file %s" % options.upload

    # Log in
    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % spw_server, verbose=0)
    spacekey = spacewalk.auth.login(spw_user,spw_pass)
    
    #
    # Process the data or whatever needs to be done go here
    #

    if not spacewalk.configchannel.channelExists(spacekey, options.channel):
        print "Configuration channel does not exist"
        spacewalk.auth.logout(spacekey)
        sys.exit(1)

    entry={
        'contents': filecontent,
        'owner': 'root',
        'group': 'root',
        'permissions': '600'
    }
    try: 
        spacewalk.configchannel.createOrUpdatePath(
            spacekey,
            options.channel,
            options.upload,
            False,
            entry
        )
    except: 
        print "Error pushing file to configchannel"
        spacewalk.auth.logout(spacekey)
        sys.exit(1)
      
    if options.push is True:
        print "Scheduling immediate deployment of channel %s" % options.channel
        spacewalk.configchannel.deployAllSystems(spacekey, options.channel)  


    # logout
    spacewalk.auth.logout(spacekey)


## MAIN
if __name__ == "__main__":
    main()  

