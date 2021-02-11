============
Music Sender (I progress, don't use yet)
============

A little app that sends music dinamically or update a music catalogue to
another device automatically.

Requirements
============

* python3.7 or latest.
* tkinter support for the gui app (tk8.6)

Installation
============

To install, type this command on the terminal. ::

   pip3 install Music_Sender/

To uninstall, type this command on the terminal. ::

   pip3 uninstall music_sender

.. note:: This commands above assume that you have pip installed in your 
   system.

How to use Music Sender app ?
=============================

Music Sender app provides two ways to be used. You can use the `Terminal 
version`_ or the `GUI version`_ or both in different machines.

Terminal version
----------------

On the terminal version, you have two modules, **server** and **client**. 
The server module is responsible to send musics to the client, and the 
client module is responsible to receive the musics. Each of them have a 
certain usage parameters. To use the modules on terminal, you have to access 
the module through the **scripts** package.

Example: ::

   python3 -m music_sender.scripts.server --local /home/user/Musics/

   python3 -m music_sender.scripts.client --local /home/user/out/ --automatic

Client usage
~~~~~~~~~~~~

   -h, --help
      Show this help message and exit.

   -v, --available
      Shows the available music catalog and theirs code numbers (e.g 120, 0, 31).

   -d, --diff
      This shows a list of musics that in server but not in client music 
      directory (sorry, I like math). This option is very useful when you want 
      make a single copy of a music you don't have.

   -a, --automatic
      Downloads the list of musics that is not in client directory.

   -l LOCAL, --local LOCAL
      This is the path the musics will be download, default is ./.

   -c COPY, --copy COPY
      Download a music from a given option, should make nothing if the option is 
      invalid.

.. note:: Be careful with the diff option. It compares the server directory 
   with client current directory (i.e The default or the choosen directory by the user).

Server usage
~~~~~~~~~~~~

   -h, --help
      Show this help message and exit.

   -l LOCAL, --local LOCAL
      Indicates where the script have to found musics.

Examples
~~~~~~~~

Starting a server...

   .. image:: images/server_script.png

Demonstration of a few actions with the client script.

   .. image:: images/client_script_1.png

   .. image:: images/client_script_2.png
   
   .. image:: images/client_script_3.png

GUI version
-----------

Unlike the Terminal mode, the GUI app is accessed through the 
``music_sender.gui.app``. In the GUI version, the server behavior is the same
as on terminal, but the client behavior difference is that the only option 
available is to make an automatic request. It's very easy to use since it 
don't have so much options to click. 

This is how it looks like.

   .. image:: images/gui_interface.png

   Client mode

   .. image:: images/gui_interface1.png

   Server mode

Examples
~~~~~~~~

Starting a server.

   .. image:: images/gui_server.png

Starting a client request

   .. image:: images/gui_client.png

Authors
=======

- Moura, 2021
