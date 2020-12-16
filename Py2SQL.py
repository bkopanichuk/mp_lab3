




class Py2SQL:
    def __init__(self):
        print("Use db_connect to connect to database")
        self.__client = None
        self.__db_name = None

    def db_connect(self, db):
        """Establish connection to postgres database"""
        self.__client = psycopg2.connect(host=db.get("HOST"), dbname=db.get("NAME"), user=db.get("USER"), password=db.get("PASSWORD"), port=db.get("PORT"))
        if self.__client:
            self.__db_name = db.get("NAME")
            print("Connection established")
        else:
            print("Connection failed")


    def db_disconnect(self):
        """Disconnect from postgres database"""
        if self.__client:
            self.__client.close()
            self.__client = None
            if self.__client:
                print("Disconnection failed")
            else:
                print("Disconnection completed")

    def db_engine(self):
        """Returns postgres engine"""
        if self.__client:
            cursor = self.__client.cursor()
            cursor.execute('SELECT version()')
            records = cursor.fetchall()
            cursor.close()
            return records[0][0]
        else:
            print("Connection not established")
            return False

    def db_name(self):
        """Returns postgres name"""
        if self.__client:
            return self.__db_name
        else:
            print("Connection not established")
            return False

    def db_size(self):
        """Returns size of postgres db"""
        if self.__client:
            cursor = self.__client.cursor()
            cursor.execute("SELECT pg_size_pretty(pg_database_size('" + self.__db_name + "'))")
            records = cursor.fetchall()
            cursor.close()
            return records[0][0]
        else:
            print("Connection not established")
            return False

    def db_tables(self):
        """Returns list of user`s tables"""
        if self.__client:
            cursor = self.__client.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
            records = cursor.fetchall()
            cursor.close()
            if (len(records) > 0):
                res = []
                for rec in records:
                    res.append(rec[0])
                return res
            else:
                return []
        else:
            print("Connection not established")
            return False

    def db_table_size(self, table):
        """Returns size of postgres db table"""
        if self.__client:
            cursor = self.__client.cursor()
            cursor.execute("SELECT pg_size_pretty(pg_total_relation_size('" + table + "'))")
            records = cursor.fetchall()
            cursor.close()
            return records[0][0]
        else:
            print("Connection not established")
            return False

    def db_table_structure(self, table):
        """Returns structure of postgres db table"""
        if self.__client:
            cursor = self.__client.cursor()
            cursor.execute("SELECT * FROM information_schema.columns WHERE table_name = '" + table + "'")
            records = cursor.fetchall()
            cursor.close()
            return records
        else:
            print("Connection not established")
            return False


    def find_table(self, table):
            """Check if table is in database"""
            if self.__client:
                cursor = self.__client.cursor()
                cursor.execute("SELECT to_regclass('" + table + "');")
                records = cursor.fetchall()
                cursor.close()
                if records[0][0] != None:
                    return True
                else:
                    return False
            else:
                print("Connection not established")
                return False

    DATA_TYPES = {'[]': 'TEXT',
                  '()': 'TEXT',
                  'frozenset': 'TEXT',
                  'set': 'TEXT',
                  '{}': 'TEXT',
                  "<class 'int'>": 'INTEGER',
                  "<class 'float'>": 'FLOAT',
                  "<class 'str'>": 'TEXT',
                  "<class 'list'>": 'TEXT',
                  "<class 'tuple'>": 'TEXT',
                  "<class 'dict'>": 'TEXT',
                  "<class 'set'>": 'TEXT',
                  "<class 'array'>": 'TEXT'}


    def __get_parent_attributes(self, py_class):
        sql_atrs = ""
        if py_class.__bases__ != ():
            for cl in py_class.__bases__:
                for attribute, value in cl.__dict__.items():
                    if not attribute.startswith("__"):
                        sql_atrs += attribute + " " + self.DATA_TYPES[str(value)] + ", "
                sql_atrs += self.__get_parent_attributes(cl)
        return sql_atrs


    def __generate_save_class_sql(self, py_class):
        sql_attributes = ""
        for attribute, value in py_class.__dict__.items():
            if not attribute.startswith("__"):
                if str(value) not in self.DATA_TYPES:
                    if not self.find_table(value.__name__):
                        self.save_class(value)
                    sql_attributes += attribute.capitalize() + "ID INTEGER REFERENCES " + value.__name__ + " (Id) ON DELETE SET NULL, "
                else:
                    sql_attributes += attribute + " " + self.DATA_TYPES[str(value)] + ", "

        sql_attributes += self.__get_parent_attributes(py_class)

        sql_attributes = sql_attributes.rstrip(', ')

        return sql_attributes

    def save_class(self, py_class):
        """Save object`s class"""
        if self.__client:
            if not self.find_table(py_class.__name__):
                sql = "CREATE TABLE " + py_class.__name__ + "(Id SERIAL PRIMARY KEY, " + self.__generate_save_class_sql(py_class) + ")"
                print(sql)
                cursor = self.__client.cursor()
                cursor.execute(sql)
                self.__client.commit()
                cursor.close()
            else:
                attrs = self.__generate_save_class_sql(py_class).split(", ")
                cursor = self.__client.cursor()
                for attr in attrs:
                    sql = "ALTER TABLE " + py_class.__name__ + " ADD COLUMN IF NOT EXISTS " + attr
                    print(sql)
                    cursor.execute(sql)
                self.__client.commit()
                cursor.close()

        else:
            print("Connection not established")
            return False

    def delete_class(self, py_class):
        """Delete class"""
        if self.__client:
            if self.find_table(py_class.__name__):
                sql = "DROP TABLE " + py_class.__name__
                cursor = self.__client.cursor()
                cursor.execute(sql)
                self.__client.commit()
        else:
            print("Connection not established")
            return False


    def __generate_save_object_sql(self, py_class):
        sql_attributes = ""
        for attribute, value in py_class.__dict__.items():
            if not attribute.startswith("__"):
                if str(value) not in self.DATA_TYPES:
                    if not self.find_table(value.__name__):
                        self.save_class(value)
                    sql_attributes += attribute.capitalize() + "ID INTEGER REFERENCES " + value.__name__ + " (Id) ON DELETE SET NULL, "
                else:
                    sql_attributes += attribute + " " + self.DATA_TYPES[str(value)] + ", "

        sql_attributes += self.__get_parent_attributes(py_class)

        sql_attributes = sql_attributes.rstrip(', ')

        return sql_attributes

    def find_object(self, py_object):
        """Find object"""
        dict = py_object.__dict__
        sql_template = ""
        for el in dict:
            if str(dict[el].__class__) in self.DATA_TYPES:
                sql_template += el + " = '" + str(dict[el]) + "' AND "
            else:
                sql_template += el + "ID = '" + str(self.find_object(dict[el])[0][0]) + "' AND "

        sql_template = sql_template.rstrip(" AND ")
        sql = "SELECT * FROM " + py_object.__class__.__name__ + " WHERE " + sql_template
        print(sql)
        cursor = self.__client.cursor()
        cursor.execute(sql)
        self.__client.commit()
        records = cursor.fetchall()
        print(records)
        return records

    def find_objects_by(self, py_class, *attributes):
        """Find object by attributes"""
        dict = attributes
        print(dict)
        sql_template = ""
        for el in dict:
            if str(el[1].__class__) in self.DATA_TYPES:
                sql_template += el[0] + " = '" + str(el[1]) + "' AND "
            else:
                sql_template += el[0]  + "ID = '" + str(self.find_object(el[1])[0][0]) + "' AND "
        sql_template = sql_template.rstrip(" AND ")
        sql = "SELECT * FROM " + py_class.__name__ + " WHERE " + sql_template
        print(sql)
        cursor = self.__client.cursor()
        cursor.execute(sql)
        self.__client.commit()
        records = cursor.fetchall()
        print(records)
        return records

    def save_object(self, py_object):
        """Save object"""
        if self.__client:
            if not self.find_table(py_object.__class__.__name__):
                self.save_class(py_object.__class__)
            if not self.find_object(py_object):
                sql_values = ""
                sql_columns = ""
                dict = py_object.__dict__
                for el in dict:
                    if str(dict[el].__class__) in self.DATA_TYPES:
                        sql_columns += el + ", "
                        sql_values += "'" + str(dict[el]) + "', "
                    else:
                        sql_columns += el + "ID, "
                        if not self.find_object(dict[el]):
                            self.save_object(dict[el])
                            sql_values += "'" + str(self.find_object(dict[el])[0][0]) + "', "
                        else:
                            sql_values += "'" + str(self.find_object(dict[el])[0][0]) + "', "
                sql_values = sql_values.rstrip(", ")
                sql_columns = sql_columns.rstrip(", ")

                sql = "INSERT INTO " + py_object.__class__.__name__ + " (" + sql_columns + ") VALUES (" + sql_values + ")"
                cursor = self.__client.cursor()
                cursor.execute(sql)
                self.__client.commit()
            else:
                sql_template = ""
                dict = py_object.__dict__
                for el in dict:
                    if str(dict[el].__class__) in self.DATA_TYPES:
                        sql_template += el + " = '" + str(dict[el]) + "', "
                    else:
                        if not self.find_object(dict[el]):
                            self.save_object(dict[el])
                            sql_template += el + "ID = '" + str(self.find_object(dict[el])[0][0]) + "', "
                        else:
                            sql_template += el + "ID = '" + str(self.find_object(dict[el])[0][0]) + "', "
                sql_template = sql_template.rstrip(", ")

                sql = "UPDATE " + py_object.__class__.__name__ + " SET " + sql_template + " WHERE id = " + str(self.find_object(py_object)[0][0])
                cursor = self.__client.cursor()
                cursor.execute(sql)
                self.__client.commit()

        else:
            print("Connection not established")
            return False

    def delete_object(self, py_object):
        """Delete object"""
        if self.__client:
            if self.find_table(py_object.__class__.__name__):
                sql = "DELETE FROM " + py_object.__class__.__name__ + " WHERE id = " + str(self.find_object(py_object)[0][0])
                cursor = self.__client.cursor()
                cursor.execute(sql)
                self.__client.commit()
        else:
            print("Connection not established")
            return False