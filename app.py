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