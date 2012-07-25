#!/usr/bin/python
# Script that creates a new channel and merges data 
#
# Author: Martin Zehetmayer <angrox@idle.at>
#
# This library is free software; you can redistribute it and/or
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
# Version Information: 
#
# 0.1 - 2012-06-22 - Martin Zehetmayer
#
#
#

# TODO: 
#    - Execption handling is completly missing
#    - Maybe merge with rhn-clone-errata.py?
#    - Get rid of the rhnget shell command and import the up2date python
#      module
#

import xmlrpclib
import httplib
import datetime
import ConfigParser
import optparse
import sys
import os

from subprocess import *
from optparse import OptionParser



def parse_args():
    parser = OptionParser()
    parser.add_option("-s", "--spw-server", type="string", dest="spw_server",
            help="Spacewalk Server")
    parser.add_option("-u", "--spw-user", type="string", dest="spw_user",
            help="Spacewalk User")
    parser.add_option("-p", "--spw-pass", type="string", dest="spw_pass",
            help="Spacewalk Password")
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords")
    parser.add_option("-c", "--src-channel", type="string", dest="src_channel",
            help="Source Channel Label: ie.\"lhm-rhel-6-x86_64\"")
    parser.add_option("-d", "--dst-channel", type="string", dest="dst_channel",
            help="Destination Channel Label: ie.\"clone-lhm-rhel-6-x86_64\"")
    parser.add_option("-e", "--dst-parent-channel", type="string", dest="dst_parent_channel",
            help="Destination parent channel label. Only needed if '--create' option is used!")
    parser.add_option("-g", "--channel-name-prefix", type="string", dest="channel_name_prefix",
            help="Prefix of the channel name. Default to 'Clone of'")
    parser.add_option("--create", action="store_true", dest="create_dst_channel", default=False,
            help="Create destination channel if it does not exist. All parameter (except the channel label) will deviated from the orginal channel")
    parser.add_option("-n", "--dry-run", action="store_true", dest="dryrun", default=False,
            help="Just print what would be done")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False)

    (options,args) = parser.parse_args()
    return options


# Create the new channel and copy the details
def create_dst_channel(spacewalk, spacekey, options):
    channel_details=spacewalk.channel.software.getDetails(spacekey, options.src_channel)
    ret=spacewalk.channel.software.create(spacekey, \
        options.dst_channel, \
        "%s %s" % (options.channel_name_prefix, channel_details['name']), \
        "%s" % channel_details['summary'] , \
        "channel-%s" % channel_details['arch_name'], \
        options.dst_parent_channel or "",
        channel_details['checksum_label'])
    if ret != 1: 
        if not options.quiet:
            print "Error creating channel!"
            spacewalk.auth.logout(spacekey)
            sys.exit(1)
    if options.verbose:
        print "Channel %s successfully created!" % options.src_channel

    new_channel_id=spacewalk.channel.software.getDetails(spacekey, options.dst_channel)['id']
    det={ \
        'description': "%s (Cloned from %s on %s)" % (channel_details['description'], options.src_channel, str(datetime.date.today())), \
        'gpg_key_url': channel_details['gpg_key_url'], \
        'gpg_key_id': channel_details['gpg_key_id'], \
        'gpg_key_fp': channel_details['gpg_key_fp'], \
        }
    ret=spacewalk.channel.software.setDetails(spacekey, new_channel_id, det)
    if ret != 1: 
        if not options.quiet:
            print "Error setting channel information!"
            spacewalk.auth.logout(spacekey)
            sys.exit(1)
    if options.verbose:
        print "Channel %s successfully edited!" % options.src_channel

        

def main():         
    # Get the options
    options = parse_args()
    # read the config
    if options.cfg_file: 
        config = ConfigParser.ConfigParser()
        config.read (options.cfg_file) 
        if options.spw_server is None:
            options.spw_server = config.get ('Spacewalk', 'spw_server')
        if options.spw_user is None:
            options.spw_user = config.get ('Spacewalk', 'spw_user')
        if options.spw_pass is None:
            options.spw_pass = config.get ('Spacewalk', 'spw_pass')

    if options.channel_name_prefix is None:
            options.channel_name_prefix = "Clone of"

    if options.src_channel is None:
        print "Source channel not given, aborting"
        sys.exit(2)
    if options.dst_channel is None:
        print "Destination channel not given, aborting"
        sys.exit(2)

    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % options.spw_server, verbose=0)
    spacekey = spacewalk.auth.login(options.spw_user, options.spw_pass)
  
    src_channel_found=0 
    dst_channel_found=0 
    dst_parent_channel_found=0 
    for channel in spacewalk.channel.listAllChannels(spacekey):
        if channel['label'] == options.src_channel:
            src_channel_found=1
            if options.verbose:
                print "Found source channel '%s'" % options.src_channel
        if channel['label'] == options.dst_channel:
            dst_channel_found=1
            if options.verbose:
                print "Found destination channel '%s'" % options.dst_channel
        if channel['label'] == options.dst_parent_channel:
            print "parent found"
            dst_parent_channel_found=1
            if options.verbose and options.create_dst_channel:
                print "Found destination parent channel '%s'" % options.dst_parent_channel

    if not src_channel_found:
        if not options.quiet:
            print "Source channel '%s' not found." % options.src_channel
        spacewalk.auth.logout(spacekey)
        sys.exit(1) 
    if dst_channel_found and options.create_dst_channel:
        if not options.quiet:
            print "Destination channel already exists! Cannot recreate it!"
        spacewalk.auth.logout(spacekey)
        sys.exit(1)
    if not dst_channel_found and not options.create_dst_channel:
        if not options.quiet:
            print "Destination channel '%s' not found and the parameter '--create' not set." % options.dst_channel
        spacewalk.auth.logout(spacekey)
        sys.exit(1)
    if options.create_dst_channel and options.dst_parent_channel and not dst_parent_channel_found:
        if not options.quiet:
            print "Destination parent channel %s not found" % options.dst_channel
        spacewalk.auth.logout(spacekey)
        sys.exit(1)
    if not dst_channel_found and options.create_dst_channel:
        if not options.quiet:
            print "Creating channel %s" % options.dst_channel
        if not options.dryrun:
            # Create Channel
            create_dst_channel(spacewalk,spacekey,options)

    # Merging packages and erratas
    if not options.quiet:
        print "Merging packages from %s into %s" % (options.src_channel, options.dst_channel)
    if not options.dryrun:
        mergepackages=spacewalk.channel.software.mergePackages(spacekey, options.src_channel, options.dst_channel)
    if not options.quiet:
        print "Merging erratas from %s into %s" % (options.src_channel, options.dst_channel)
    if not options.dryrun:
        mergeerrata=spacewalk.channel.software.mergeErrata(spacekey, options.src_channel, options.dst_channel)

    if not options.quiet:
        print "Done"
    spacewalk.auth.logout(spacekey)


## MAIN
if __name__ == "__main__":
    main()  

