import tornado.ioloop
import tornado.web
# from pymongo import MongoClient
from motor.motor_tornado import MotorClient
import os
from tornado import gen
from collections import Counter


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<a href="/instance/?name=doctor">By instance</a><br/>')
        self.write('<a href="/class/?name=doctor">By class</a><br/>')
        self.write('<a href="/common/?names=doctor,surgeon">Common classes</a><br/>')

def unique(tuples):
    prev_key = None
    for t in sorted(tuples, key=lambda t: t["_id"]):
        key = (t["_id"], t["instance"], t["class"])
        if prev_key is None or prev_key != key:
            yield t
        prev_key = key

@gen.coroutine
def search(query):
    client = MotorClient()
    db = client.tuplesdb
    collectionNames = yield db.collection_names()
    results = []
    for collectionName in collectionNames:
        future = db[collectionName].aggregate([
            { "$match": query },
            { "$sort": { "frequency": -1 } },
            { "$limit": 30 }
        ], 
            allowDiskUse=True
        ).to_list(None)
        results.append(future)
    results = yield results
    tuples = unique(sorted([t for r in results for t in r], key=lambda t: t["frequency"], reverse=True)[:100])
    raise gen.Return(tuples)

class InstanceHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        name = self.get_argument("name")
        tuples = yield search({"instance": name})
        self.render("instance.html", tuples=tuples)

@gen.coroutine
def getCommonClasses(names):
    classes = {}
    for idx, name in enumerate(names.split(",")):
        tuples = yield search({"instance": name})
        if idx == 0:
            classes = dict([(t["class"], t["frequency"]) for t in tuples])
        else:
            keep = set()
            for t in tuples:
                if t["class"] in classes:
                    classes[t["class"]] += t["frequency"]
                    keep.add(t["class"])
            for clazz in set(classes.keys()) - keep:
                del classes[clazz]
    raise gen.Return(classes)

class CommonClassesHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        names = self.get_argument("names")
        classes = yield getCommonClasses(names)
        self.render("commonclasses.html", classes=classes)

class ContinueHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        names = self.get_argument("names")
        classes = yield getCommonClasses(names)
        instances = Counter()

        for clazz, _ in sorted(classes.iteritems(), key=lambda (c, cnt): cnt, reverse=True)[:10]:
            if clazz == "thing":
                continue
            print "Searching for class " + clazz
            tuples = yield search({"class": clazz, "frequency": { "$gt": 5 }})
            for t in tuples:
                instances[t["instance"]] += 1
        self.render("commonclasses.html", classes=instances)        

class ClassHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        name = self.get_argument("name")
        tuples = yield search({"class": name, "frequency": { "$gt": 5 }})
        self.render("instance.html", tuples=tuples)

def make_app():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/instance/", InstanceHandler),
        (r"/class/", ClassHandler),
        (r"/common/", CommonClassesHandler),
        (r"/continue/", ContinueHandler),
    ], 
        template_path=os.path.join(dir_path, "webtemplates"),
        debug=True,
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
