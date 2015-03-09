#!/usr/bin/python
# Script that syncs RPM packages from the Red Hat Network to a local
# Spacewalk Server
#
# Author: Martin Zehetmayer <angrox@idle.at>
#
# This script uses code and the same configuration file from the 
# rhn-clone-errata.py script from Andy Speagle <andy.speagle@wichita.edu>
# which can be found in the official spacewalk git repostiory
# The script depends on the mrepo package from Dag Wiers which can be found
# on http://dag.wieers.com/home-made/mrepo/
#
# THANKS both of you for your great work! 
#
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


import xmlrpclib
import httplib
import datetime
import ConfigParser
import optparse
import sys
import os
import rpmUtils.miscutils

from subprocess import *
from optparse import OptionParser



class ProxiedTransport(xmlrpclib.Transport):
    def set_proxy(self, proxy):
        self.proxy = proxy
    def make_connection(self, host):
        self.realhost = host
        h = httplib.HTTP(self.proxy)
        return h
    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))
    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)


def rhnget(chan, filename, options):
    if os.path.exists("%s/%s" % (options.download_dir, filename)):
        if options.verbose:
            print "  - File %s already downloaded" % filename
        return "%s/%s" % (options.download_dir, filename)
    rhngetcmd="/usr/bin/rhnget --filter=%s --systemid=%s rhns:///%s %s" % (filename, options.sysid_file, chan, options.download_dir)
    if options.proxy:
        proxy_def={"http_proxy": "http://%s" % options.proxy, "https_proxy": "http://%s" % options.proxy}
        rhngetproc = Popen(rhngetcmd, shell=True,stdout=PIPE, stderr=PIPE, env=proxy_def)
    else:
        rhngetproc = Popen(rhngetcmd, shell=True,stdout=PIPE, stderr=PIPE)
    output=rhngetproc.communicate()[0]
    if rhngetproc.returncode != 0:
        if not options.quiet:
            print "  - Not succeeded"
            print output
    return "%s/%s" % (options.download_dir, filename)


def spwpush(chan, local_filename, options):
    spwpushcmd="/usr/bin/rhnpush --server %s -u %s -p %s -c %s %s" % (options.spw_server, options.spw_user, options.spw_pass, chan, local_filename)
    print spwpushcmd
    spwpushproc = Popen(spwpushcmd, shell=True,stdout=PIPE, stderr=PIPE)
    output=spwpushproc.communicate()[0]
    if spwpushproc.returncode != 0:
        if not options.quiet:
            print "  - Not succeeded"
            print output
    else:
        os.unlink(local_filename)


def parse_args():
    parser = OptionParser()
    parser.add_option("-s", "--spw-server", type="string", dest="spw_server",
            help="Spacewalk Server")
    parser.add_option("-S", "--rhn-server", type="string", dest="rhn_server",
            help="RHN Server (rhn.redhat.com)")
    parser.add_option("-u", "--spw-user", type="string", dest="spw_user",
            help="Spacewalk User")
    parser.add_option("-p", "--spw-pass", type="string", dest="spw_pass",
            help="Spacewalk Password")
    parser.add_option("-U", "--rhn-user", type="string", dest="rhn_user",
            help="RHN User")
    parser.add_option("-P", "--rhn-pass", type="string", dest="rhn_pass",
            help="RHN Password")
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords, downloaddir")
    parser.add_option("-c", "--src-channel", type="string", dest="src_channel",
            help="Source Channel Label: ie.\"rhel-x86_64-server-6\"")
    parser.add_option("-g", "--system-id-file", type="string", dest="sysid_file",
            help="systemid file. Can be generated with 'gensystemid' from the mrepo package")
    parser.add_option("-d", "--download-dir", type="string", dest="download_dir",
            help="Directory to hold the temporary downloaded rpm packages")
    parser.add_option("-b", "--begin-date", type="string", dest="bdate",
            help="Beginning Date: ie. \"1900-01-01\" (defaults to \"1900-01-01\")")
    parser.add_option("-e", "--end-date", type="string", dest="edate",
            help="Ending Date: ie. \"1900-12-31\" (defaults to TODAY)")
    parser.add_option("-i", "--publish", action="store_true", dest="publish", default=False,
            help="Publish packages (into destination channels). Default is download-only")
    parser.add_option("-n", "--newest-only", action="store_true", dest="newest", default=False,
            help="Download only newest packages per-repo. Default is download all.")
    parser.add_option("-x", "--proxy", type="string", dest="proxy",
            help="Proxy server and port to use (e.g. proxy.company.com:3128)")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False)

    (options,args) = parser.parse_args()
    return options


def main():         
    # Get the options
    options = parse_args()
    # read the config
    if options.cfg_file is None:
        print "Need a configurations file!"
        print "Try use the --help option!"
        sys.exit(2)
        
    config = ConfigParser.ConfigParser()
    config.read (options.cfg_file)

    if options.spw_server is None:
        options.spw_server = config.get ('Spacewalk', 'spw_server')
    if options.spw_user is None:
        options.spw_user = config.get ('Spacewalk', 'spw_user')
    if options.spw_pass is None:
        options.spw_pass = config.get ('Spacewalk', 'spw_pass')
    if options.rhn_server is None:
        options.rhn_server = config.get ('RHN', 'rhn_server')
    if options.rhn_user is None:
        options.rhn_user = config.get ('RHN', 'rhn_user')
    if options.rhn_pass is None:
        options.rhn_pass = config.get ('RHN', 'rhn_pass')
    if options.proxy is None:
        try:
            options.proxy = config.get ('Global', 'proxy')
        except:
            pass
    if options.download_dir is None:
        options.download_dir = config.get ('Global', 'download_dir')
    chanMap = {}

    if options.src_channel is None:
        print "Source channel not given, aborting"
        sys.exit(2)

    if options.sysid_file is None:
        print "Missing system id file, aborting"
        sys.exit(2)

    chanMap[options.src_channel] = config.get('ChanMap', options.src_channel)

    if options.proxy is not None:
        p = ProxiedTransport()
        p.set_proxy(options.proxy)
        rhn = xmlrpclib.Server("https://%s/rpc/api" % options.rhn_server, verbose=0, transport=p)
    else:
        rhn = xmlrpclib.Server("https://%s/rpc/api" % options.rhn_server, verbose=0)
        
    rhnkey = rhn.auth.login(options.rhn_user, options.rhn_pass)

    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % options.spw_server, verbose=0)
    spacekey = spacewalk.auth.login(options.spw_user, options.spw_pass)
    
    date_end=options.edate or str(datetime.date.today())
    date_start=options.bdate or "1900-01-01"

    for chan in chanMap:
        if chanMap[chan] is None:
            print "Invalid Channel!"
            sys.exit(2)

        if not options.quiet:
            print "+ Starting to sync %s to %s on %s" % (chan, chanMap[chan], options.spw_server)
            print "+ Checking all available packages in the spacewalk server"
        # Get ALL the spacewalk channel packages
        packages=spacewalk.channel.software.listAllPackages(spacekey, chanMap[chan])
        space_packages=[]
        for pkg in packages:
            # TODO: Do we have to take care of the epoch field? 
            pkg_file_name="%s-%s-%s.%s.rpm" % (pkg['name'], pkg['version'], pkg['release'], pkg['arch_label'])
            if options.verbose:
                print "  - SPACE: %s - %s" % (pkg['name'], pkg_file_name)
            space_packages.append(pkg_file_name)

        # Get RHEL package information for a specific timeslot and compare the packages with the one already synced
        if not options.quiet:
            print "+ Checking all available packages in the Red Hat Network (%s - %s) " % (date_start, date_end)
        packages=rhn.channel.software.listAllPackages(rhnkey, chan, date_start, date_end)
        
        # Get only the latest version of packages from RHN.
        if options.newest:
            if not options.quiet:
                print "+ Proccessing only newest available packages."
            highdict = {}
            for pkg in packages:
                if (pkg['package_name'],  pkg['package_arch_label']) not in highdict:
                    highdict[(pkg['package_name'],  pkg['package_arch_label'])] = pkg
                else:
                    pkg2 = highdict[(pkg['package_name'],  pkg['package_arch_label'])]
                    if cmp(pkg['package_name'],  pkg2['package_name']) == 0:
                        if rpmUtils.miscutils.compareEVR((pkg['package_epoch'],pkg['package_version'],pkg['package_release']),(pkg2['package_epoch'],pkg2['package_version'],pkg2['package_release'])) > 0:
                            highdict[(pkg['package_name'],  pkg['package_arch_label'])] = pkg
            if len(highdict):
                packages = []
                for pkg in highdict:
                    packages.append(highdict[pkg])

        # Confirm package isn't in SpaceWalk
        rhn_packages=[]
        for pkg in packages:
            # TODO: Do we have to take care of the epoch field? 
            pkg_file_name="%s-%s-%s.%s.rpm" % (pkg['package_name'], pkg['package_version'], pkg['package_release'], pkg['package_arch_label'])
            if options.verbose:
                print "  - RHN: %s - %s" % (pkg['package_name'], pkg_file_name)
            if pkg_file_name not in space_packages:
                if options.verbose:
                    print "    - We need to sync %s" % pkg_file_name
                rhn_packages.append(pkg_file_name)

        # Sync the packages
        if not options.quiet:
            print "+ Sync and upload the packages"
        for pkg in rhn_packages:
            if not options.quiet:
                print "+ Sync %s" % pkg
            local_filename=rhnget(chan, pkg, options)
            if not options.quiet:
                print "+ Upload %s" % pkg
            if options.publish:
                spwpush(chanMap[chan], local_filename, options)
            else:
                if not options.quiet:
                    print " - No packages will be uploaded. Missing parameter -i"
        if not options.quiet:
            print "+ Done"


    rhn.auth.logout(rhnkey)
    spacewalk.auth.logout(spacekey)


## MAIN
if __name__ == "__main__":
    main()  

