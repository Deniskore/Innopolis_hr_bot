from unqlite import UnQLite
import json


class db:
    def __init__(self):
        self.__db = UnQLite('bot.udb')
        pass

    def get(self, key):
        if self.__db.exists(str(key)):
            return json.loads(self.__db[str(key)].decode('utf-8'))
        else:
            return None

    def is_exists(self, key):
        return self.__db.exists(str(key))

    def set(self, key, obj):
        self.__db[str(key)] = json.dumps(obj)
        self.__db.commit()

    def remove(self, key):
        self.__db.delete(self.__db[(str(key))])
        self.__db.commit()


db = db()
