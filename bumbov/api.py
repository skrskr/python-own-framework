import inspect
import os

from parse import parse
from webob import Request
from requests import Session as RequestSession
from whitenoise import WhiteNoise
from wsgiadapter import WSGIAdapter as RequestsWISGIAdapter
from jinja2 import Environment, FileSystemLoader

from .middleware import Middleware
from .response import Response

class API:

    def __init__(self, template_dir="templates", static_dir="static"):
        self.routes = {}

        self.template_env = Environment(
            loader=FileSystemLoader(os.path.abspath(template_dir))
        )
        self.exception_handler = None
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

        self.middleware = Middleware(self)


    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]

        if path_info.startswith("/static"):
            environ["PATH_INFO"] = path_info[len("/static"):]
            return self.whitenoise(environ, start_response)
        
        return self.middleware(environ, start_response)


    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)

    def test_session(self, base_url="http://testserver"):
        session = RequestSession()
        session.mount(prefix=base_url, adapter=RequestsWISGIAdapter(self))
        return session

    def add_route(self, path, handler, allowed_methods=None):
        assert path not in self.routes, f"Route {path} already exists"
        if allowed_methods is None:
            allowed_methods = ["get", "post", "put", "delete", "head", "options", "patch"]
        self.routes[path] = {"handler": handler, "allowed_methods": allowed_methods}
    
    def route(self, path, allowed_methods=None):
        assert path not in self.routes, f"Route {path} already exists"

        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler
        return wrapper

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not Found"
        return response

    def find_handler(self, request_path):
        for path, handler_data in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler_data, parse_result.named
        return None, None

    def handle_request(self, request):
        response = Response()
        try:
            handler_data, kwargs = self.find_handler(request.path)
            if handler_data is not None:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method not allowed", request.method)

                else:
                    if request.method.lower() not in allowed_methods:
                        raise AttributeError("Method not allowed", request.method)

                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)
        
        return response

    def template(self, template_name, context=None):
        if context is None:
            context = {}
        
        return self.template_env.get_template(template_name).render(**context)

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler