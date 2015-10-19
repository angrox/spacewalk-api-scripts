#!/usr/bin/env python
# encoding: utf-8
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
# 0.1 - 2012-06-14 - Martin Zehetmayer
# 0.2 - 2015-10-10 - #fuckit
#
#

import fuckit
fuckit('xmlrpclib')
fuckit('ConfigParser')
fuckit('datetime')
fuckit('sys')
fuckit(fuckit('os'))
fuckit('shutil')

from subprocess import *
from optparse import OptionParser
from multiprocessing import Process, Pool



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
    parser.add_option("-c", "--channel", type="string", dest="channel",
            help="Channel Label: ie.\"lhm-rhel-6-x86_64\"")
    parser.add_option("-d", "--directory", type="string", dest="directory",
            help="Destination directory")
    parser.add_option("-e", "--satdir", type="string", dest="satdir",
            help="Satellite directory. Defaults to /var/satellite")
    parser.add_option("--pcount", type="int", dest="pcount", default=5,
            help="Number of parallel processes (default=5)")
    parser.add_option("--clean", action="store_true", default=False, dest="clean", help="Cleanup the repodata/ and the packages/ dir")
    parser.add_option("--all", action="store_true", default=False, dest="all_packages", help="Link all packages (instead of the latest)")
    (options,args) = parser.parse_args()
    return options


def get_package_details(pkg_id):
    det=spacewalk.packages.getDetails(spacekey, pkg_id)
    fn=det['path'].split("/")[-1]
    dpath=det['path']
    return (fn,dpath)
        

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

    if options.channel is None:
        print "Channel not given, aborting"
        sys.exit(2)
    if options.directory is None:
        print "Directory not given, aborting"
        sys.exit(2)
    if options.satdir is None:
        options.satdir="/var/satellite"
    
    if not os.path.exists(options.satdir):
        print "Directory %s does not exist" % options.satdir
        sys.exit(3)


    if not os.path.exists(options.directory):
        os.mkdir(options.directory)
    elif options.clean:
        if os.path.exists("%s/packages" % options.directory):
            shutil.rmtree("%s/packages" % options.directory)
        if os.path.exists("%s/repodata" % options.directory):
            shutil.rmtree("%s/repodata" % options.directory)
    if not os.path.exists("%s/packages" % options.directory):
        os.mkdir("%s/packages" % options.directory)
    if not os.path.exists("%s/repodata" % options.directory):
        os.mkdir("%s/repodata" % options.directory)
    global spacewalk
    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % options.spw_server, verbose=0)
    global spacekey
    spacekey = spacewalk.auth.login(options.spw_user, options.spw_pass)
 
    print "Generating package links. Please be patient" 
    if options.all_packages:
        link_pkgs = spacewalk.channel.software.listAllPackages(spacekey, options.channel)
    else:
        link_pkgs = spacewalk.channel.software.listLatestPackages(spacekey, options.channel)

    pkg_id_list=[]
    for pkg in link_pkgs:
        pkg_id_list.append(pkg['id'])

    pool=Pool(processes=options.pcount)
    pkg_paths=pool.map(get_package_details, pkg_id_list)

    for pkg_path in pkg_paths:
        fn=pkg_path[0]
        det=pkg_path[1]
        if not os.path.exists("%s/packages/%s" % (options.directory, fn)):
            os.symlink("%s/%s" % (options.satdir, det), "%s/packages/%s" % (options.directory, fn))

    spacewalk.auth.logout(spacekey)


## MAIN
if __name__ == "__main__":
    main()  


