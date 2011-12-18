function(doc) {
    var docid = doc._id;
    return (docid.match("^t/") == "t/");
}
