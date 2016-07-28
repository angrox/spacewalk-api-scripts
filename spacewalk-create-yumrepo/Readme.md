What is this script for?

This script takes a channel and links all packages assosiated with it to a local directory.
This directory can be used as a yum repo directory (after issuing createrepo on it)

Usage
-----
<pre>
Usage: spacewalk-create-yumrepo.py [options]

Options:
  -h, --help            show this help message and exit
  -s SPW_SERVER, --spw-server=SPW_SERVER
                        Spacewalk Server
  -u SPW_USER, --spw-user=SPW_USER
                        Spacewalk User
  -p SPW_PASS, --spw-pass=SPW_PASS
                        Spacewalk Password
  -f CFG_FILE, --config-file=CFG_FILE
                        Config file for servers, users, passwords
  -c CHANNEL, --channel=CHANNEL
                        Channel Label: ie."lhm-rhel-6-x86_64"
  -d DIRECTORY, --directory=DIRECTORY
                        Destination directory
  -e SATDIR, --satdir=SATDIR
                        Satellite directory. Defaults to /var/satellite
  --pcount=PCOUNT       Number of parallel processes (default=5)
  --clean               Cleanup the repodata/ and the packages/ dir
  --all                 Link all packages (instead of the latest)
</pre>
