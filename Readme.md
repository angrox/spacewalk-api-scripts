spacewalk-api-scripts
=====================

What is this?
-------------
These are a few scripts which utilize the spacewalk api to perform various tasks. 
For we all have (mostly) the same problems or requirements I will publish all scripts
I wrote to perform recurring or annoying tasks. 


Scripts
-------
* spacewalk-rhn-sync -- Sync packages from the Red Hat Network and pushes it to the spacewalk server. Uses mrepo! 
* spacewalk-orgclone-channel -- Clones a channel and its errata to a new channel. This works even if the channel is shared from another organization.
* spacewalk-create-yumrepo -- Creates a yum repository out of an spacewalk channel
* uln-clone-errata -- Fetches errata information for oracles "unbreakable" red hat clone and pushes it into spacewalk
