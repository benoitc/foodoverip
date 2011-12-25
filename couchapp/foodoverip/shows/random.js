function(doc, req) {
    var ddoc = this;
    var Mustache = require("lib/mustache"),
    path = require("lib/path").init(req);



    if (!doc) {
        // old url
        if (req.id && req.id.match("^t/t/")) {
            var docid = req.id.split("/")[2];
            log("reqid: " + req.id);
            log("docid: " + docid);
            var redirect_url = path.absolute(path.rewrite() + "/" + docid);
            log("redirect_url: " + redirect_url);
            return {
                code: 301,
                headers: {"Location": redirect_url},
                body: "Redirected to " + redirect_url
            };
        }

        return "please reload " + req.id;

    }


    var templates = ddoc.templates;
    var docid = doc._id.replace("/", "%2F"),
        href = doc._id.replace("t/", "");


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

    var uri = path.absolute(path.rewrite() + "/" + href)


    provides("html", function() {
        return Mustache.to_html(templates.food, {
            doc: doc,
            root: path.rewrite(),
            photo_uri: photo_uri,
            profile_uri: profile_uri,
            vhost: req.headers['x-couchdb-vhost-path'],
            is_location: is_location,
            coords: coords,
            uri: uri,
            href: href
        });
    });
}
