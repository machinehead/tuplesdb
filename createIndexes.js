db = db.getSiblingDB('tuplesdb');
db.getCollectionNames().forEach(function(collection) {
    print("Now indexing " + collection);
    db.getCollection(collection).createIndex({ "instance": 1, "class": 1 });
    db.getCollection(collection).createIndex({ "class": 1 });
});
