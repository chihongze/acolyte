"""本模块包含tornado application对象的创建，
   以及WSGI钩子，您也可以直接通过该模块来启动API服务
"""
import tornado.ioloop
import tornado.web
import tornado.wsgi
from acolyte.core.bootstrap import EasemobFlowBootstrap
from acolyte.api import BaseAPIHandler
from acolyte.api.route import URL_MAPPING


def load_config():
    return {"rest_api": {"port": 8888}}


config = load_config()


def make_app():
    # 先初始化应用所需要的资源
    bootstrap = EasemobFlowBootstrap()
    bootstrap.start(config)
    BaseAPIHandler.service_container = bootstrap.service_container
    return tornado.web.Application(URL_MAPPING, debug=True)


app = make_app()
wsgi_app = tornado.wsgi.WSGIAdapter(app)


def main():
    app.listen(config["rest_api"]["port"])
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
