============
Music Sender
============

A little app that sends music dinamically or update a music catalogue to
another device automatically. The scripts that composes the application is
"client.py" and "server.py". These scripts were created to be independent and
with the capability of running in any machine (See also `Dependencies`_).

Command line arguments
======================

Server
------

    -h, --help
        Show this help message and exit.

    -l LOCAL, --local LOCAL
        Indicates where the script have to find musics.

Client
------

    -h, --help
        show this help message and exit.

    -v, --available
        shows the available music catalog and theirs code numbers
        (e.g 120, 0, 31).

    -c COPY, --copy COPY
        download a music from a given option, should make nothing if the 
        option is invalid.

    -d, --diff
        This shows a list of musics that in server but not in client music
        directory (sorry, I like math). This option is very useful when you
        want make a single copy of a music you don't have.

    -a, --automatic
        Downloads the list of musics that is not in client directory.

    -l LOCAL, --local LOCAL
        This is the path the musics will be download, default is ./.

How to use
==========

Terminal
--------

Server
~~~~~~
Given the options in `Command line arguments`_, start your server.
Here an example of what you can do.

    .. image:: images/server_commandline_sample.png

In the command above, you just asking to the server script to get musics from
the "~/Musics" or "/home/user/Musics" directory. When you click enter you 
should see this output.

    .. image:: images/working_server.png
        
Great, that means that our server is running and he's ready to send musics to 
any client.

.. note:: You don't need to start a server in a only-music directory, the 
          server script will automatically filter the musics and send the 
          correct indexes to the client. You can initialize the server in a 
          empty directory too, but this is not useful (since you want to send 
          musics instead of nothing).

Client
~~~~~~
Since the server is working, you can turn on the client script in another 
device and make some requests.

With the client script, you can request a simple file, request an list of the 
available music on the server or the list of musics that are missing in the 
client directory and make an automatic download (i.e request the musics that 
aren't in the client directory).
See an example...

    .. image:: images/client_available_command.png

This command above asks to the server the available musics on it. When you 
click enter you should see this output.

    .. image:: images/client_available_output.png

Similarly, there's a "diff" option (i.e It shows the missing musics in the 
client directory).

    .. image:: images/client_diff_output.png

.. note:: Remember that the diff option compare the client directory (i.e the 
          choosen directory where the musics will be downloaded), so it's 
          recommended to use the "--local" option.
    
.. image:: images/client_diff_and_local.png

After that, you can request a music by his code, with the "copy" option:

    .. image:: images/client_copy_output.png

You can request an automatic action too that will download all the missing 
musics (the previous note about "diff" option applies to the "automatic" 
option since he use the "diff" option to download only the necessary files).

    .. image:: images/client_automatic_output.png

In case the server doesn't contain any music file, for any command the output 
will look like this (except "copy" option).

    .. image:: images/client_not_music.png

Or in the case the client cannot connect to the server, that is the following 
output.

    .. image:: images/client_error.png

User interface app
------------------

Coming out soon.
    
Dependencies
============

    * utils.py
    * python >= 3.7
