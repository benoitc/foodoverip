function(doc, req) {
    var ddoc = this;

    if (!doc) {
        return "please reload";
    }

    var Mustache = require("lib/mustache"),
        path = require("lib/path").init(req);


    var templates = ddoc.templates;
   
    photo_uri = path.rewrite() + "/photo/" + doc._id.replace("/", "%2F"); 

    provides("html", function() {
        return Mustache.to_html(templates.food, {
            doc: doc,
            photo_uri: photo_uri,
            vhost: req.headers['x-couchdb-vhost-path'] 
        });
    });
}
