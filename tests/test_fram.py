import pytest
from api import API
from middleware import Middleware


FILE_DIR="css"
FILE_NAME="main.css"
FILE_CONTENTS="body {background-color: red}"

# helpers
def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)
    return asset



def test_basic_route_adding(api):
    @api.route("/home")
    def home(req, res):
        res.text = "TEXT"


def test_route_overlap_throw_exception(api):

    @api.route("/home")
    def home(req, res):
        res.text = "TEXT"
    
    with pytest.raises(AssertionError):
        @api.route("/home")
        def home(req, res):
            res.text = "TEXT"


def test_client_can_send_requests(api, client, base_url):
    RESPONSE_TEXT = "TEXT"

    @api.route("/test")
    def test(req, res):
        res.text = RESPONSE_TEXT
    
    response = client.get(base_url + "/test")
    assert response.text == RESPONSE_TEXT


def test_parameterize_route(api, client, base_url):
    @api.route("/test/{name}")
    def test(req, res, name):
        res.text = f"Hello {name}"
    
    response = client.get(base_url + "/test/John")
    assert response.text == "Hello John"


def test_404_not_found(client, base_url):
    response = client.get(base_url + "/not-found")
    assert response.status_code == 404
    assert response.text == "Not Found"


def test_class_based_handler(api,client, base_url):
    RESPONSE_TEXT = "TEXT"
    @api.route("/test")
    class TestHandler:
        def get(self, req, res):
            res.text = RESPONSE_TEXT
        def post(self, req, res):
            res.text = RESPONSE_TEXT

    response = client.get(base_url + "/test")
    assert response.text == RESPONSE_TEXT
    response = client.post(base_url + "/test")
    assert response.text == RESPONSE_TEXT


def test_class_based_handler_method_not_allowed(api,client, base_url):
    @api.route("/test")
    class TestHandler:
        def post(self, req, res):
            res.text = "TEXT"

    with pytest.raises(AttributeError):
        client.get(base_url + "/test")


def test_alternative_route(api, client, base_url):
    RESPONSE_TEXT = "TEXT"

    def handler(req, res):
        res.text = RESPONSE_TEXT

    api.add_route("/test", handler)
    response = client.get(base_url + "/test")
    assert response.text == RESPONSE_TEXT
    

def test_template(api, client, base_url):
    
    @api.route("/html")
    def html_handler(req, res):
        res.body = api.template("index.html", context={
            "title":"Some Title",
            "name":"Some Name"
        }).encode()

    response = client.get(base_url + "/html")
    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text


def test_custom_exception_handler(api, client, base_url):
    def on_exception(req, res, exc):
        res.text = "AttributeErrorHappened"

    api.add_exception_handler(on_exception)

    @api.route("/test")
    def test(req, res):
        raise AttributeError()
    
    response = client.get(base_url + "/test")
    assert response.text == "AttributeErrorHappened"

# staticfiles tests


def test_404_is_returned_for_nonexistent_static_file(client):
    assert client.get(f"http://testserver/main.css").status_code == 404


def test_assets_are_served(tmpdir_factory, base_url):
    static_dir = tmpdir_factory.mktemp("static")
    _create_static(static_dir)
    api = API(static_dir=static_dir)
    client = api.test_session()

    response = client.get(f"{base_url}/static/{FILE_DIR}/{FILE_NAME}")
    assert response.text == FILE_CONTENTS
    assert response.status_code == 200


def test_middleware_methods_are_called(api, client, base_url):
    process_request_called = False
    process_response_called = False

    class CallMiddlewareMethods(Middleware):

        def __init__(self, app):
            super().__init__(app)

        def process_request(self, req):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, req, resp):
            nonlocal process_response_called
            process_response_called = True

    
    api.add_middleware(CallMiddlewareMethods)
    
    @api.route("/test")
    def test(req, res):
        res.text = "TEXT"

    client.get(f"{base_url}/test")
    assert process_request_called == True
    assert process_response_called == True
