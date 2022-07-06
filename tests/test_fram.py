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

