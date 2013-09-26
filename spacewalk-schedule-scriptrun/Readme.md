spacewalk-remove-old-packages.py
===============================

What is this script for? 
------------------------

 This script schedules a job for one registered client within Spacewalk. Useful
 when you do not have another orchestration software like Puppet Mcollective. 
 Needs OSAD activated on the client server and configured to run scripts


Usage
-----

<pre>

Usage: spacewalk-schedule-scriptrun.py [options]

Options:
  -h, --help            show this help message and exit
  -f CFG_FILE, --config-file=CFG_FILE
                        Config file for servers, users, passwords. Defaults to
                        '/etc/rhn/rhn-api-user.conf'
  -s SYSTEM, --system=SYSTEM
                        System to schedule the script run
  -r RUNID, --runid=RUNID
                        Gets the returncode of a job. This option is mutually
                        exclusive to all options except configfile and help
</pre>

The configuration file must be parseable bei ConfigParser:<br>
Example: 

<pre>
[Spacewalk]
spw_server = spacewalk.example.com
spw_user   = api_user_1
spw_pass   = api_password_1
</pre>


Activating OSAD on the client machines
--------------------------------------

* yum -y install osad
* service osad start
* chkconfig osad on
* rhn-action-control --enable-run

