import pytest


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
        })

    response = client.get(base_url + "/html")
    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text