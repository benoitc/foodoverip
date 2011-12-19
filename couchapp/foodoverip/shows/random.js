function(doc, req) {
    var ddoc = this;

    if (!doc) {
        return "please reload";
    }

    var Mustache = require("lib/mustache"),
        path = require("lib/path").init(req);


    var templates = ddoc.templates;
    var docid = doc._id.replace("/", "%2F");

   
    var photo_uri = path.rewrite() + "/photo/" + docid;
    var profile_uri  = path.rewrite() + "/avatar/" + docid;

    var coords = null,
        is_location = false;
    if (doc.source.geo) {
        is_location = true;
        coords = { 
            "lon": doc.source.geo.coordinates[0],
            "lat": doc.source.geo.coordinates[1]
        };
    }

    var uri = path.absolute(path.rewrite() + "/" + docid)

    
    provides("html", function() {
        return Mustache.to_html(templates.food, {
            doc: doc,
            root: path.rewrite(),
            photo_uri: photo_uri,
            profile_uri: profile_uri,
            vhost: req.headers['x-couchdb-vhost-path'],
            is_location: is_location,
            coords: coords,
            uri: uri     
        });
    });
}
