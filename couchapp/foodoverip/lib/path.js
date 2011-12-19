// from couch.js
function encodeOptions(options) {
  var buf = [];
  if (typeof(options) == "object" && options !== null) {
    for (var name in options) {
      if (!options.hasOwnProperty(name)) {continue;}
      var value = options[name];
      if (name == "key" || name == "startkey" || name == "endkey") {
        value = JSON.stringify(value);
      }
      buf.push(encodeURIComponent(name) + "=" + encodeURIComponent(value));
    }
  }
  if (!buf.length) {
    return "";
  }
  return "?" + buf.join("&");
}

function concatArgs(array, args) {
  for (var i=0; i < args.length; i++) {
    array.push(args[i]);
  };
  return array;
};

function makePath(array) {
  var options, path;
  
  if (typeof array[array.length - 1] != "string") {
    // it's a params hash
    options = array.pop();
  }
  path = array.map(function(item) {return encodeURIComponent(item)}).join('/');
  if (options) {
    return path + encodeOptions(options);
  } else {
    return path;    
  }
};
exports.makePath = makePath;

function parseUri(sourceUri){
   /* parseUri by Steven Levithan (http://badassery.blogspot.com) */
    var uriPartNames = ["source","protocol","authority","domain","port","path","directoryPath","fileName","query","anchor"];
    var uriParts = new RegExp("^(?:([^:/?#.]+):)?(?://)?(([^:/?#]*)(?::(\\d*))?)?((/(?:[^?#](?![^?#/]*\\.[^?#/.]+(?:[\\?#]|$)))*/?)?([^?#/]*))?(?:\\?([^#]*))?(?:#(.*))?").exec(sourceUri);
    var uri = {};
    
    for(var i = 0; i < 10; i++){
        uri[uriPartNames[i]] = (uriParts[i] ? uriParts[i] : "");
    }
    
    // Always end directoryPath with a trailing backslash if a path was present in the source URI
    // Note that a trailing backslash is NOT automatically inserted within or appended to the "path" key
    if(uri.directoryPath.length > 0){
        uri.directoryPath = uri.directoryPath.replace(/\/?$/, "/");
    }
    
    return uri;
}
exports.parseUri = parseUri;


function req_path(req, part) {
    if (req.headers['x-couchdb-vhost-path']) {
        return [''];
    } else {
        var p = req.path;
        return ['', p[0], p[1] , p[2], part];
    }    
}

exports.init = function(req) {
  return {
    asset : function() {
      var parts = req_path(req, []);
      return makePath(concatArgs(parts, arguments));
    },
    show : function() {
      var parts = req_path(req, '_show');
      return makePath(concatArgs(parts, arguments));
    },
    list : function() {
      var parts = req_path(req, '_list');
      return makePath(concatArgs(parts, arguments));
    },
    update : function() {
      var parts = req_path(req, '_update');
      return makePath(concatArgs(parts, arguments));
    },
    rewrite: function() {
      var parts = req_path(req, '_rewrite');
      return makePath(concatArgs(parts, arguments));
    },

    absolute : function(path) {
      return 'http://' + req.headers.Host + path;
    }
  }
};

