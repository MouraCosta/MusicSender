Music Sender
============

This project is useful for updating your music directory without connecting 
your usb in the computer.

How to use
==========

First you need to set your server. The server must be in the local where your musics are.

* Server commands

    -h, --help  show this help message and exit
    -l LOCAL, --local LOCAL  Indicates where the script have to found musics

After that, init your client.

* Client commands

    -h, --help  show this help message and exit
    -v, --available  returns the available music catalog
    -c COPY, --copy COPY  request a copy from a given option, should make nothing if the option is invalid
    -d, --diff  This shows a list of musics that in server but not in client music directory
    -a, --automatic  create a list of musics that is not in client directory
    -l LOCAL, --local LOCAL  This is where the musics will be received, default is ./

    *Be Careful*, the diff option will compare the server music directory with the client current directory if
    you don't specify the LOCAL argument. The same applies for the --automatic option. Your command line should 
    look like this.::

        python client.py -l [PATH] -[d | a | c]
        
    This script can be in any place, since the default directory is *./*.
