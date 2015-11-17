#!/usr/bin/python
# encoding: utf-8
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
import yaml

from optparse import OptionParser
from distutils.version import LooseVersion


ci_dict= {}

def parse_args():
    parser = OptionParser()
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords. Defaults to '/etc/rhn/rhn-api-user.conf'")
    parser.add_option("-c", "--custominfo-file", type="string", dest="custominfo_file",
            help="Yaml file containing the custominfo data")
    
    #
    # Put other options here
    #

    (options,args) = parser.parse_args()
    return options


def parseCustomInfo(sysname):
    for (key,val) in ci_dict.iteritems(): 
        if key == 'override':
            continue
        if re.search(val['regex'], sysname, flags=re.IGNORECASE):
            return ( key, val['syscontact'], val['adprimary'], val['adsecondary'], val['adtertiary'])


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
    if options.custominfo_file is None: 
        print "Missing argument: custominfo file. See -h"
        sys.exit(1)

    # Try to read the yaml file
    global ci_dict
    try:
        cif=open(options.custominfo_file, 'r')
        ci_dict=yaml.safe_load(cif)
        cif.close()
    except:
        print "Could not open or parse %s." % options.custominfo_file

    # Log in
    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % spw_server, verbose=0)
    spacekey = spacewalk.auth.login(spw_user,spw_pass)
    
    #
    # Process the data or whatever needs to be done go here
    #

    allsystems = spacewalk.system.listSystems(spacekey)
    for entry in allsystems:
        custominfo=0
        # Check Override
        for (key, val) in ci_dict['override'].iteritems():
            for o_server in val['systems']:
                if re.search(o_server, entry['name']):
                    print "- Found override information for %s" % o_server
                    print "  - %s - %s, %s (%s, %s), %s" % (entry['name'], val['syslocation'], val['adprimary'], val['adsecondary'], val['adtertiary'], key)
                    custominfo = {'syscontact': key, 'syslocation': val['syslocation'], 'adprimary': val['adprimary'], 'adsecondary': val['adsecondary'], 'adtertiary': val['adtertiary']} 
        if custominfo == 0:
            try: 
                (syslocation, syscontact, adprimary, adsecondary, adtertiary) = parseCustomInfo(entry['name'])
                print "- %s - %s, %s %s, (%s, %s)" % (entry['name'], syslocation, syscontact, adprimary, adsecondary, adtertiary)
            except:
                print "- System %s failed! Using value 'unkown'" % entry['name']
                syslocation = 'unknown'
                syscontact = 'unknown'
                adprimary = 'not.specified'
                adsecondary = 'not.specified'
                adstertiary = 'not.specified'
            custominfo={'syscontact': syscontact, 'syslocation': syslocation, 'adprimary': adprimary, 'adsecondary': adsecondary, 'adtertiary': adtertiary} 
        ret=spacewalk.system.setCustomValues(spacekey, entry['id'], custominfo)
        if ret == 1:
            print "   - System %s successfully updated" % entry['name']
        else:
            print "   - Could not update system %s !" % entry['name']


    # logout
    spacewalk.auth.logout(spacekey)


## MAIN
if __name__ == "__main__":
    main()  

