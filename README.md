smate
=====

Simple Sublime Text 2 plugin a-la RMATE for TextMate 2
Works over SFTP plugin.

This plugin works on Mac OS X, but not tested under another operating systems.

INSTALL AND USAGE.
=====
0. Install SFTP plugin (using Package Control, for example)
    0.1. Create new server in sftp.

1. Clone this repository to your $SUBLIME_PATH/Packages
    1.1. Optional: Restart Sublime Text 2 and press ctrl+` Find something like
            '[smate] Server started...'

2. Copy smate-client.py to remote server.

3. Create ~/.ssh/config with following text:
    | Host <name for your host>
    |     Hostname <addr>
    |     RemoteForward 52693 127.0.0.1:52693

4. Run ssh under your terminal:
    $ ssh <name for your host>

5. Run sftp under sublime text 2 and load some file.
    /* sftp creates temporary dirs in this point. smate uses them but doesn't
            create. this will be fixed in next versions */

6. Inside ssh session run
    $ ./smate-client.py -hostname <hostname in sftp> <filename>

This file had to be opened in sublime text 2

CONFIGURING
=====
smate-client could get options from enviroment:
    SMATE_HOSTNAME: server name in sftp plugin
    SMATE_PORT: port for connection. default is 52693 (must be changed there,
            in ~/.ssh/config and in smate plugin settings)
    SMATE_NO_DATA: if set, files won't be transferred using smate. smate will
            only create the files in your local filesystem and tell sftp to sync
            this file with the server.

smate config:
    port: port for connection. default is 52693 (must be changed there,
            in ~/.ssh/config and in smate-client settings)
    force_sync_on_download: if set to true, all files will be loaded using sftp.
            if false, only files without data
    default_sftp_server: if set, all requests without hostname will be
            interpreted as requests from this sftp server (instead of
            smate-client -hostname or $SMATE_HOSTNAME)
    host: localhost. do not change this

KNOWN BUGS
=====
If connection is weak, smate server might down and do not set up :(

