#!/usr/bin/env python
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
# schedules a scriptrun on a given host 
#
# Version Information: 
#
# 0.2 - 2015-10-10 - #fuckit
#

import fuckit
fuckit('xmlrpclib')
fuckit('ConfigParser')
fuckit(fuckit('optparse'))
fuckit('sys')
fuckit('os')
fuckit('re')

from optparse import OptionParser
from select import select
from datetime import datetime
from datetime import timedelta




def parse_args():
    parser = OptionParser()
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords. Defaults to '/etc/rhn/rhn-api-user.conf'")
    parser.add_option("-s", "--system", type="string", dest="system",
            help="System to schedule the script run")
    parser.add_option("-r", "--runid", type="int", dest="runid",
            help="Gets the returncode of a job. This option is mutually exclusive to all options except configfile and help")
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

    if options.system is None and options.runid is None:
        print "Missing option: system or runid. Check -h (help)"
        sys.exit(1)

    if options.runid is None:
        rlist, _, _ = select([sys.stdin], [], [], 2)
        if rlist:
            script=sys.stdin.read()
        else:
            print "No input. Please pipe the script to be executed into the spacewalk script!"
            sys.exit(1)

    # Log in
    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % spw_server, verbose=0)
    spacekey = spacewalk.auth.login(spw_user,spw_pass)

    
    
    #
    # Process the data or whatever needs to be done go here
    #
    # Check if system exists

    
    if options.runid is not None:
        try: 
            jobdetails=spacewalk.system.getScriptActionDetails(spacekey, options.runid)
        except xmlrpclib.Fault, err:
            print "Error finding runid (Code %s, %s)" % (err.faultCode, err.faultString)
            spacewalk.auth.logout(spacekey)
            sys.exit(1)
        if not jobdetails['result']:
            spacewalk.auth.logout(spacekey)
            sys.exit(2)
        
        spacewalk.auth.logout(spacekey)
        if jobdetails['result'][0]['returnCode'] != 0:
            sys.exit(1)
        sys.exit(0)
    else: 
        try: 
            systementry=spacewalk.system.getId(spacekey, options.system)
        except xmlrpclib.Fault, err:
            print "Error finding system (Code %s, %s)" % (err.faultCode, err.faultString)
            spacewalk.auth.logout(spacekey)
            sys.exit(1)
        if not systementry:
            print "System %s not found." % options.system
            spacewalk.auth.logout(spacekey)
            sys.exit(1)
        else:
            systemid=systementry[0]['id']

        # We need an xmlrpc.DateTime instance (iso8601). To get one we calculate the runtime
        # with datetime objects and transoform them into a timetuple and then transform it 
        # again with the xmlrpclib.DateTime() function.
        # Thanks Red Hat & Fedora Team for not documenting this! 
        rundate=xmlrpclib.DateTime((datetime.today()+timedelta(minutes=5)).timetuple())

        try:  
            # Hardcoded: Run as root/root with 10 sec timeout
            runid=spacewalk.system.scheduleScriptRun(spacekey, systemid, 'root', 'root', 
                10, script, rundate )
        except xmlrpclib.Fault, err:
            print "Error scheduling scriptrun (Code %s, %s)" % (err.faultCode, err.faultString)
            spacewalk.auth.logout(spacekey)
            sys.exit(1)

        print runid
    # logout
    spacewalk.auth.logout(spacekey)
    sys.exit(0)


## MAIN
if __name__ == "__main__":
    main()  

