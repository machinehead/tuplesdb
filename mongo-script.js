db = db.getSiblingDB('tuplesdb')
db.getCollectionNames().forEach(function(collection) {
    db.getCollection(collection).find({ $or: [
	    {"class": "professional"},
	    {"class": "employee"},
	    { "instance": "lvn" },
	    { "instance": "lpn" },
	    { "instance": "rn" },
	    { "instance": "engineer" },
	    { "instance": "doctor" },
	    { "instance": "physician" }
    ]}).forEach(function(doc) {
        doc["collection"] = collection;
        printjsononeline(doc);
    });
})
