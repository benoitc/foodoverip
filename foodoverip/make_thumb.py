# -*- coding: utf-8 -

import os
import time
import argparse
import ConfigParser
from io import BytesIO

import couchdbkit
import Image

max_width = 210
height = 150

def get_db(server_uri, db_name):
    s = couchdbkit.Server(server_uri)
    return s.get_or_create_db(db_name)

def make_thumb(db):
    res = db.view("foodoverip/food", include_docs=True)
    for row in res:
        doc = row.get('doc')
        atts = doc.get('_attachments', {})

        if 'photo.png' in atts and not 'photo_thumb1.png' in atts:
            print "make thumb for %s" % doc['_id']
            photo = db.fetch_attachment(doc, 'photo.png')
            img = Image.open(BytesIO(photo))
            ratio = 1
            if img.size[0] > max_width:
                ratio = max_width / float(img.size[0])
            elif img.size[1] > max_height:
                ratio = max_height / float(img.size[1])

            w = img.size[0] * ratio
            h = img.size[1] * ratio

            thumb = img.resize((int(w), int(h)), Image.ANTIALIAS)
            tout = BytesIO()
            thumb.save(tout, 'png')
            tout.seek(0)

             # send it to couchdb
            db.put_attachment(doc, tout, "photo_thumb.png",
                headers={'Transfer-Encoding': 'chunked'})



def run():
    parser = argparse.ArgumentParser(
            description='grab foodoverip images from twiiter')

    parser.add_argument(
        '-c',
        type=str,
        default="",
        help="""\
            Path to the config file.
            """)

    args = parser.parse_args()

    db_name = 'foodoverip'
    server_uri = 'http://127.0.0.1:5984'

    if args.c:
        config_path = os.path.expanduser(args.c)
        if os.path.exists(config_path):
            config = ConfigParser.ConfigParser()
            config.read(args.c)
            if config.has_option('foodoverip', 'server_uri'):
                server_uri = config.get('foodoverip', 'server_uri')

            if config.has_option('foodoverip', 'db'):
                db_name = config.get('foodoverip', 'db')

    db = get_db(server_uri, db_name)

    make_thumb(db)


if __name__ == '__main__':
    run()
