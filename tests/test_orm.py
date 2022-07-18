import sqlite3


def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_define_tables(Author, Book):
    assert Author.name.type == str
    assert Author.age.type == int

    assert Book.author.table == Author
    
    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"


def test_create_tables(db, Author, Book):
    db.create(Author)
    db.create(Book)

    assert Author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT)"
    assert Book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT)"

    for table in ("author", "book"):
        assert table in db.tables


def test_create_author_instance(db, Author):
    db.create(Author)
    author = Author(name="John Doe", age=42)
    
    assert author.name == "John Doe"
    assert author.age == 42
    assert author.id is None


def test_save_author_instance(db, Author):
    db.create(Author)
    author = Author(name="John Doe", age=42)
    db.save(author)

    assert author._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [42, "John Doe"]
    )

    assert author.id is 1

    author2 = Author(name="John Doe2", age=35)
    db.save(author2)

    assert author2.id is 2

    author3 = Author(name="John Doe3", age=44)
    db.save(author3)

    assert author3.id is 3


def test_query_all_authors(db, Author):
    db.create(Author)

    john = Author(name="John Doe", age=23)
    vik = Author(name="Vik Star", age=43)
    db.save(john)
    db.save(vik)
    
    authors = db.all(Author)

    assert Author._get_select_all_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", "name"]
    )
    assert len(authors) == 2
    assert type(authors[0]) == Author
    assert {a.age for a in authors} == {23, 43}
    assert {a.name for a in authors} == {"John Doe", "Vik Star"}


def test_get_author(db, Author):
    db.create(Author)

    john = Author(name="John Doe", age=23)
    db.save(john)
    author = db.get(Author, id=1)

    assert Author._get_select_where_sql(id=1) == (
        "SELECT id, age, name FROM author WHERE id = ?;",
        ["id", "age", "name"],
        [1]
    )
    assert type(author) == Author
    assert author.name == "John Doe"
    assert author.age == 23
    assert author.id == 1


def test_get_book(db, Author, Book):
    db.create(Author)
    db.create(Book)

    john = Author(name="John Doe", age=23)
    db.save(john)
    book = Book(author=john, published=2020, title="My Book")
    db.save(book)

    jack = Author(name="jack Doe", age=25)
    db.save(jack)
    book2 = Book(author=jack, published=2020, title="My Book22")
    db.save(book2)

    book = db.get(Book, id=1)

    assert book.title == "My Book"
    assert book.author.name == "John Doe"
    assert book.author.id == 1


def test_get_all_books(db, Author, Book):
    db.create(Author)
    db.create(Book)

    john = Author(name="John Doe", age=23)
    db.save(john)
    book = Book(author=john, published=2020, title="My Book")
    db.save(book)

    jack = Author(name="jack Doe", age=25)
    db.save(jack)
    book2 = Book(author=jack, published=2020, title="My Book22")
    db.save(book2)

    books = db.all(Book)

    assert len(books) == 2
    assert books[1].author.name == "jack Doe"


def test_update_author(db, Author):
    db.create(Author)

    john = Author(name="John Doe", age=23)
    db.save(john)

    john.name = "John Doe2"
    john.age = 42
    db.update(john)

    john_from_db = db.get(Author, id=1)

    assert john_from_db.name == "John Doe2"
    assert john_from_db.age == 42