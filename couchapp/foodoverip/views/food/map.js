function(doc) {
    var docid = doc._id,
        atts = doc._attachments;

    if ((docid.match("^t/") == "t/") && 
            (typeof(atts['photo.png']) != "undefined")) {
        emit(doc._id, null);
    } 
}
