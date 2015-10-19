#!/usr/bin/env python
# encoding: utf-8
# Fetches the ULN Errata from Oracle and syncs it in an existing
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
# Version Information: 
#
# 0.1 - 2012-07-06 - Martin Zehetmayer
# 0.2 - 2015-10-10 - #fuckit
#
#       Initial release. Ugly code. But hey - it works! :) 
#       PS.: Now it definitely works. Thank you, #fuckitpy!

import fuckit
fuckit('xmlrpclib')
fuckit('ConfigParser')
fuckit(fuckit('optparse'))
fuckit('sys')
fuckit('re')
fuckit('datetime')

from rhn import rpclib


# Fetches the ULN erratas
def get_uln_erratas(channel, proxy, suffix, arch, year):
    s = rpclib.Server(uri="https://linux-update.oracle.com/XMLRPC",proxy="http://%s" % proxy)
    errataList = s.errata.getErrataByChannel(channel)
    sorted_errata={}
    for errata in errataList:
        if re.search("-%s-" % year, errata["id"]) is not None:
            suffix_id="%s%s" % (errata["id"], suffix)
            if not suffix_id in sorted_errata:
                sorted_errata[suffix_id]={}
                sorted_errata[suffix_id]["packages"]=["%s-%s-%s.%s" % (errata["name"], errata["version"], errata["release"], arch)]
                sorted_errata[suffix_id]["type"]=errata["type"]
                sorted_errata[suffix_id]["summary"]=errata["summary"]
                sorted_errata[suffix_id]["description"]=errata["description"]
            else:
                sorted_errata[suffix_id]["packages"].append("%s-%s-%s.%s" % (errata["name"], errata["version"], errata["release"], arch))
    return sorted_errata

# Get spacewalk packages. We need them compared to the packages listed in the uln errata information
def get_spacewalk_packages(spacekey,spacewalk,channel):
    packages=spacewalk.channel.software.listAllPackages(spacekey, channel)
    space_packages={}
    for pkg in packages:
        # TODO: Do we have to take care of the epoch field? 
        pkg_file_name="%s-%s-%s.%s" % (pkg['name'], pkg['version'], pkg['release'], pkg['arch_label'])
        space_packages[pkg_file_name]=pkg['id']
    return space_packages

# Get existing channel erratas
def get_channel_errata_ids(spacekey,spacewalk,channel):
    space_erratas=spacewalk.channel.software.listErrata(spacekey, channel)
    space_errata_ids=[]
    for errata in space_erratas:
        space_errata_ids.append(errata["advisory_name"])
    return space_errata_ids



def parse_args():
    parser = OptionParser()
    parser.add_option("-s", "--spw-server", type="string", dest="spw_server",
            help="Spacewalk Server")
    parser.add_option("-u", "--spw-user", type="string", dest="spw_user",
            help="Spacewalk User")
    parser.add_option("-p", "--spw-pass", type="string", dest="spw_pass",
            help="Spacewalk Password")
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords, downloaddir")
    parser.add_option("-c", "--uln-channel", type="string", dest="uln_channel",
            help="ULN Channel Label, ex \"ol6_x86_64_latest\", \"el5_x86_64_latest\"")
    parser.add_option("-d", "--spw-channel", type="string", dest="spw_channel",
            help="Channel label in spacewalk")
    parser.add_option("-a", "--arch", type="string", dest="arch",
            help="Channel architecture. Defaults to x86_64")
    parser.add_option("-x", "--proxy", type="string", dest="proxy",
            help="Proxy server and port to use (e.g. proxy.company.com:3128)")
    parser.add_option("-e", "--errata-suffix", type="string", dest="suffix",
            help="Suffix to errata string, defaults to \"\"")
    parser.add_option("-y", "--year", type="string", dest="year",
            help="Sync Erratas from specific year. Default to the current year")
    parser.add_option("-n", "--dryrun", action="store_true", dest="dryrun", default=False,
            help="Do NOT upload errata to server (but everything else)")

    (options,args) = parser.parse_args()
    return options


def main():
    advisory_type_trans= { 'SECURITY': 'Security Advisory', 'ENHANCEMENT': 'Product Enhancement Advisory', 'BUG': 'Bug Fix Advisory'}
    # Get the options
    options = parse_args()
    # read the config
    config = ConfigParser.ConfigParser()
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
    if options.proxy is None:
        options.proxy = config.get ('Global', 'proxy')


    if options.suffix is None:
        options.suffix=""

    if options.arch is None:
        options.arch="x86_64"
    if options.year is None:
        options.year=datetime.date.today().year

    if options.uln_channel is None:
        print "ULN channel not given, aborting"
        sys.exit(2)

    if options.spw_channel is None:
        print "SPW channel not given, aborting"
        sys.exit(2)

    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % options.spw_server, verbose=0)
    spacekey = spacewalk.auth.login(options.spw_user, options.spw_pass)

    print "- Check available packages in spacewalk"
    space_packages=get_spacewalk_packages(spacekey,spacewalk,options.spw_channel)
    print "- Getting spacewalk errata advisory names"
    space_erratas=get_channel_errata_ids(spacekey,spacewalk,options.spw_channel)
    print "- Getting ULN errata data"
    uln_erratas=get_uln_erratas(options.uln_channel, options.proxy, options.suffix, options.arch, options.year)
    errata_to_sync=[] 
    present_pkgs2id={}
    print "- Compare which erratas to sync"
    for errata in uln_erratas:
        for errata_pkg in uln_erratas[errata]["packages"]:
            if errata_pkg in space_packages:
                present_pkgs2id[errata_pkg]=space_packages[errata_pkg]
                if not errata in errata_to_sync:
                    if not errata in space_erratas:
                        errata_to_sync.append(errata)
    
    print "- Starting sync" 
    for errata in errata_to_sync:
        pkgids=[]
        errata_info={}
        bug_info=[]
        keywords=[]
        
        pkgtxt="\n\nPackages:\n"
        for pkg in uln_erratas[errata]["packages"]:
            if pkg in present_pkgs2id:
                pkgids.append(present_pkgs2id[pkg])
                pkgtxt="%s %s\n" % (pkgtxt, pkg)
        errata_info["synopsis"]=uln_erratas[errata]["summary"]
        errata_info["errataFrom"]="Oracle Inc."
        errata_info["description"]=uln_erratas[errata]["description"][0:3999]
        errata_info["advisory_name"]=errata
        errata_info["advisory_type"]=advisory_type_trans[uln_erratas[errata]["type"]]
        errata_info["solution"]="Update to following packages:\n%s" % pkgtxt
        errata_info["notes"]="na"
        errata_info["topic"]=uln_erratas[errata]["summary"]
        errata_info["product"]=options.spw_channel
        errata_info["advisory_release"]=1
        print "- Publish errata %s to %s" % (errata, options.spw_channel)
        if not options.dryrun:
            spacewalk.errata.create(spacekey, errata_info, bug_info, keywords, pkgids, True, [options.spw_channel])
        else:
            print "  + Dryrun - done nothing"
       
    print "- All done!" 
    spacewalk.auth.logout(spacekey)



## MAIN
if __name__ == "__main__":
    main()  
