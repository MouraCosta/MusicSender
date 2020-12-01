Music Sender
============

This project is useful for updating your music directory without connecting 
your usb in the computer.

How to use
==========

First you need to set your server. You should configure the path where the 
server script need to find musics.

* Server commands

    -h, --help  show this help message and exit
    -l LOCAL, --local LOCAL  Indicates where the script have to find musics

After that, init your client.

* Client commands

    -h, --help  show this help message and exit
    -v, --available  shows the available music catalog and theirs code numbers (e.g 120, 0, 31)
    -c COPY, --copy COPY  download a music from a given option, should make nothing if the option is invalid
    -d, --diff  This shows a list of musics that in server but not in client music directory (sorry, I like math).
                This option is very useful when you want make a single copy of a music you don't have.
    -a, --automatic  downloads the list of musics that is not in client directory.
    -l LOCAL, --local LOCAL  This is the path the musics will be download, default is ./

    *Be careful*, the diff option will compare the server music directory with the client current directory if
    you don't specify the LOCAL argument. The same applies for the --automatic option. Your command line should 
    look like this.::

        python client.py -l [PATH] -[d | a | c]
        
    This script can be in any place, since the default directory is *./*.
