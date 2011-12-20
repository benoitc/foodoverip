# foodoverip

Foodoverip is a simple service allowing you to share your food photos
over twitter.

Foodoveripis powered by Apache CouchDB and Python. All the frontend is a
couchapp.


## Requirements

- Apache CouchDB , better to use [The distribution
  rcouch](http://github.com/refuge/rcouch) proposed by the
[refuge](http://refuge.io) project.
- [couch_randomdoc](http://github.com/refuge/couch_randomdoc) extention
  to handle random document fetching in couchdb. It's already included
in rcouch.
- [Python 2.7](http://python.orh)
- [Couchdbkit](http://couchdbkit.org)
- [Gevent](http://gevent.org)
- [Erica](http://github.com/benoitc/erica)


## Installation

1. Install rcouch and launch it.
2. push the couchapp to your rcouch

    $ cd couchapp/foodoverip
    $ erica push http://rcouch/foodoverip

3. Launch the food grabber

    $ go_grab_food -c ~/.foodoverip.ini 

ex of ini:

    [foodoverip]
    server_uri = http://127.0.0.1:5984 ; uri of couchdb node
    db = foodoverip ; db where to save data
    q = #foodoverip ; query to do in twitter
    refresh_tim = 10 ; in seconds
