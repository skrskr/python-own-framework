from api import API

app = API()


@app.route("/home")
def home(request, response):
    response.text = "Hello From HOME page"


# @app.route("/home")
# def home2(request, response):
#     response.text = "Hello From HOME page"

@app.route("/about")
def about(request, response):
    response.text = "Hello From About page"


@app.route("/hello/{name}")
def say_hello(request, response, name):
    response.text = f"Hello, {name}"


@app.route("/sum/{num_1:d}/{num_2:d}")
def sum(request, response, num_1, num_2):
    total = int(num_1) + int(num_2)
    response.text = f"{num_1} + {num_2} = {total}"


@app.route("/books")
class BookHandler:
    def get(self, req, res):
        res.text = "GET:// Hello From Books page"

    def post(self, req, res):
        res.text = "POST:// Endpoint to create new book"
    
    def put(self, req, res):
        res.text = "PUT:// Endpoint to update book"

    def delete(self, req, res):
        res.text = "DELETE:// Endpoint to delete book"


def sample(req, res):
    res.text = "Hello From Sample page"

app.add_route("/sample", sample)