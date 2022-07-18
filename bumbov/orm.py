import sqlite3
import inspect


class Database:

    def __init__(self, path) -> None:
        self.conn = sqlite3.Connection(path)

    @property
    def tables(self):
        SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type='table'"
        return [row[0] for row in self.conn.execute(SELECT_TABLES_SQL).fetchall()]

    def create(self, table):
        self.conn.execute(table._get_create_sql())

    def save(self, instance):
        sql, values = instance._get_insert_sql()
        cursor = self.conn.execute(sql, values)
        instance._data["id"] = cursor.lastrowid
        self.conn.commit()

    def all(self, table):
        sql, fields = table._get_select_all_sql()
        rows = self.conn.execute(sql).fetchall()
        result = []
        for row in rows:
            instance = table()
            for field, value in zip(fields, row):
                if field.endswith("_id"):
                    field = field[:-3]
                    fk = getattr(table, field)
                    value = self.get(fk.table, id=value)
                setattr(instance, field, value)
            result.append(instance)
        
        return result

    def get(self, table, id):
        sql, fields, params = table._get_select_where_sql(id)
        row = self.conn.execute(sql, params).fetchone()
        if row is None:
            raise Exception(f"{table.__name__} instance with id {id} does not exist")

        instance = table()
        for field, value in zip(fields, row):
            if field.endswith("_id"):
                field = field[:-3]
                fk = getattr(table, field)
                value = self.get(fk.table, id=value)
            setattr(instance, field, value)
        
        return instance

    
    def update(self, instance):
        sql, values = instance._get_update_sql()
        self.conn.execute(sql, values)
        self.conn.commit()

    def delete(self, instance, id):
        sql, params = instance._get_delete_sql(id)
        self.conn.execute(sql, params)
        self.conn.commit()


class Table:

    def __init__(self, **kwargs):
        self._data = {
            "id": None
        }

        for key, value in kwargs.items():
            self._data[key] = value

    def __getattribute__(self, key):
        _data = super().__getattribute__("_data")
        if key in _data:
            return _data[key]
        return super().__getattribute__(key)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in self._data:
            self._data[key] = value

    @classmethod
    def _get_create_sql(cls):
        CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS {name} ({fields})"

        fields = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT"
        ]

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(f"{name} {field.sql_type}")
            elif isinstance(field, ForeignKey):
                fields.append(f"{name}_id INTEGER")

        fields = ", ".join(fields)
        name = cls.__name__.lower()
        return CREATE_TABLE_SQL.format(name=name, fields=fields)


    
    def _get_insert_sql(self):
        INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
        cls = self.__class__
        fields = []
        placeholders = []
        values = []

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append("?")
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
                values.append(getattr(self, name).id)
                placeholders.append("?")

        fields = ", ".join(fields)
        placeholders = ", ".join(placeholders)

        sql = INSERT_SQL.format(name=cls.__name__.lower(), fields=fields, placeholders=placeholders)

        return sql, values

    @classmethod
    def _get_select_all_sql(cls):
        SELECT_ALL_SQL = "SELECT {fields} FROM {name};"
        fields = ["id"]

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
        
        name = cls.__name__.lower()
        sql = SELECT_ALL_SQL.format(fields=", ".join(fields), name=name)
        return sql, fields

    @classmethod
    def _get_select_where_sql(cls, id):
        SELECT_WHERE_SQL = "SELECT {fields} FROM {name} WHERE id = ?;"
        fields = ["id"]
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
        
        name = cls.__name__.lower()
        sql = SELECT_WHERE_SQL.format(fields=", ".join(fields), name=name)
        params = [id]
        return sql, fields, params

    def _get_update_sql(self):

        UPDATE_SQL = "UPDATE {name} SET {fields} WHERE id = ?;"
        cls = self.__class__

        fields = []
        values = []
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(f"{name} = ?")
                values.append(getattr(self, name))
            elif isinstance(field, ForeignKey):
                fields.append(f"{name}_id = ?")
                values.append(getattr(self, name).id)

        values.append(getattr(self, 'id'))
        sql = UPDATE_SQL.format(name=cls.__name__.lower(), fields=', '.join(fields))
        return sql, values

    @classmethod
    def _get_delete_sql(cls, id):
        DELETE_SQL = "DELETE FROM {name} WHERE id = ?;"
        sql = DELETE_SQL.format(name=cls.__name__.lower())
        params = [id]
        return sql, params


class Column:
    
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        SQLITE_TYPE_MAP = {
            str: "TEXT",
            int: "INTEGER",
            bool: "INTEGER",
            float: "REAL",
            bytes: "BLOB",
        }
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:
    def __init__(self, table):
        self.table = table
