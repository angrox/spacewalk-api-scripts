What is this script for? 
------------------------

The script spacewalk-orgchannel-clone is used to clone a channel which is shared from another organization.
This task is not possible using the GUI.

The shell script build_spacewalk_baseline is used to clone a complete channel structure and give
them a specific prefix. This can be used to create a baseline channel for periodic update cycles.


Usage
-----
<pre>
age: spacewalk-orgclone-channel.py [options]

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
  -c SRC_CHANNEL, --src-channel=SRC_CHANNEL
                        Source Channel Label: ie."lhm-rhel-6-x86_64"
  -d DST_CHANNEL, --dst-channel=DST_CHANNEL
                        Destination Channel Label: ie."clone-lhm-
                        rhel-6-x86_64"
  -e DST_PARENT_CHANNEL, --dst-parent-channel=DST_PARENT_CHANNEL
                        Destination parent channel label. Only needed if '--
                        create' option is used!
  -g CHANNEL_NAME_PREFIX, --channel-name-prefix=CHANNEL_NAME_PREFIX
                        Prefix of the channel name. Default to 'Clone of'
  --create              Create destination channel if it does not exist. All
                        parameter (except the channel label) will deviated
                        from the orginal channel
  -n, --dry-run         Just print what would be done
  --latest-only         Only merge the latest version of the packages found in
                        the parent channel
  -v, --verbose         
  -q, --quiet           
</pre>
