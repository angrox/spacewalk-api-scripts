#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:tw=79:ai:expandtab

import xmlrpclib
import httplib
import datetime
import ConfigParser
import optparse
import sys
import os


import xml.dom.minidom

from optparse import OptionParser

DEFAULT_XML_FILE = "/etc/rhn/spacewalk-channel-hierarchy.xml"

def parse_args():
    parser = OptionParser()
    parser.add_option("-x", "--xml-file", type="string", dest="xml_file",
            help="XML file for describing the channel hierarchy in the\
            Spacewalk server. Defaults to '" + DEFAULT_XML_FILE + "'")
    parser.add_option("-U", "--update-parent", type="string",
            dest="update", help="The parent channel which is to be\
            updated, or 'ALL'.")
   


    parser.add_option("-s", "--spw-server", type="string", dest="spw_server",
            help="Spacewalk Server")
    parser.add_option("-u", "--spw-user", type="string", dest="spw_user",
            help="Spacewalk User")
    parser.add_option("-p", "--spw-pass", type="string", dest="spw_pass",
            help="Spacewalk Password")
    parser.add_option("-f", "--config-file", type="string", dest="cfg_file",
            help="Config file for servers, users, passwords")

    parser.add_option( "-n", "--dry-run", action="store_true", dest="dryrun",
            default=False, help="Just print what would be done" )
    parser.add_option( "-v", "--verbose", action="store_true", dest="verbose",
            default=False )
    parser.add_option( "-q", "--quiet", action="store_true", dest="quiet",
            default=False )


    #
    # Put other options here
    #

    (options,args) = parser.parse_args()
    return options

def performSync(src_channel,dst_channel):
    # Merging packages and erratas
    if not options.quiet:
        print "Merging packages from %s into %s" % (src_channel, dst_channel)
    if not options.dryrun:
        mergepackages=spacewalk.channel.software.mergePackages(spacekey, src_channel, dst_channel)
    if not options.quiet:
        print "Merging errata from %s into %s" % (src_channel, dst_channel)
    if not options.dryrun:
        mergeerrata=spacewalk.channel.software.mergeErrata(spacekey, src_channel, dst_channel)

def checkAvailability(chan):
    found = False
    for availableChan in allAvailableChannels:
        chanLabel=availableChan['label']
        if (chanLabel == chan):
            found = True
    return(found)
            
def updateChannels(knoten,parentToUpdate):
    for parentEntry in knoten.getElementsByTagName("parent"):
        if ( ( parentEntry.attributes['dest'].value == parentToUpdate ) |
        ( parentToUpdate == "ALL" ) ):
            pSource=parentEntry.attributes['source'].value
            pDest=parentEntry.attributes['dest'].value

            if not options.quiet:
                print ( " + Parent: " + pSource + " -> " + pDest )
            if ( checkAvailability(pSource) == False ):
                die ( " Source channel " + pSource + " not found!" )
            if ( checkAvailability(pDest) == False ):
                die ( " Destination channel " + pDest + " not found!" )
            performSync(pSource, pDest)

            for childEntry in parentEntry.getElementsByTagName("child"):
                cSource=childEntry.attributes['source'].value
                cDest=childEntry.attributes['dest'].value

                if not options.quiet:
                    print ( " - Child: " + cSource + " -> " + cDest + ".")
                if ( checkAvailability(cSource) == False ):
                    die ( "Source channel " + cSource + " not found!" )
                if ( checkAvailability(cDest) == False ):
                    die ( "Destination channel " + cDest + " not found!" )
                performSync(cSource, cDest)

            print ( "" )


    if not options.quiet:
        print "Done"


def die(Message):
    print Message
    spacewalk.auth.logout(spacekey)
    sys.exit(1)

def main():         
    # Get the options
    global options
    options = parse_args()
    # read the config
    
    if options.update is None:
        print ( "Neither ALL nor a specific parent channel for update\
 given.\nExiting..." )
        sys.exit(1)

    if options.cfg_file:
        config = ConfigParser.ConfigParser()
        config.read (options.cfg_file)
        if options.spw_server is None:
            options.spw_server = config.get('Spacewalk', 'spw_server')
        if options.spw_user is None:
            options.spw_user = config.get('Spacewalk', 'spw_user')
        if options.spw_pass is None:
            options.spw_pass = config.get('Spacewalk', 'spw_pass')

    if options.xml_file is None:
        options.xml_file=DEFAULT_XML_FILE

    datei = open(options.xml_file, "r")
    dom = xml.dom.minidom.parse(datei)
    datei.close()

    global spacewalk
    spacewalk = xmlrpclib.Server("https://%s/rpc/api" % options.spw_server, verbose=0)
    global spacekey
    spacekey = spacewalk.auth.login(options.spw_user, options.spw_pass)
    global allAvailableChannels
    allAvailableChannels = spacewalk.channel.listAllChannels(spacekey)
    updateChannels(dom, options.update)
    spacewalk.auth.logout(spacekey)

## MAIN
if __name__ == "__main__":
    main()
