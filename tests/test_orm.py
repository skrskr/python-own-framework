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
    