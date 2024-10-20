import tornado.web
import tornado.ioloop
from auth_handler import AuthHandler
from retrieve_handler import RetrieveHandler
from reindex_handler import ReindexHandler
from index_handler import IndexHandler

def make_app():
    return tornado.web.Application([
        (r"/auth", AuthHandler),
        (r"/retrieve", RetrieveHandler),
        (r"/reindex", ReindexHandler),
        (r"/index", IndexHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    print("Server started on port 8000")
    tornado.ioloop.IOLoop.current().start()