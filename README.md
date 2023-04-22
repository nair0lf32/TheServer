# theServer

This is the most basic implementation of a server in python

I just wanted to do it!  

Using socket programming instead of http server module directly (one-liner)

it serves a simple default page  (plus a silly 404)

Rewritten to use OOP following this example [here](https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch/)

This is very basic (obviously) and lack alot of things like:

- security ( the best production environment ever, if you don't care about the data)
- multiple connection handling
- full http (cache, cookies, CORS, sessions...)
- daemon,wsgi,logging...

## Usage

This script requires `python3` (tested with version 3.9)

To start the server use:

`python server.py`

Then connect to the address it serves at (default: `http://127.0.0.1:2311`)
