import pymongo


class MongoSessionHelper:
    def __init__(self, host='127.0.0.1', port=27017):
        self.__host = host
        self.__port = port
        self.__session = pymongo.MongoClient(host=self.__host, port=self.__port)

    def get_active_session(self):
        return self.__session

    def get_active_db(self, db_name: str):
        return self.__session.get_database(db_name)

    def get_active_collection(self, db_name: str, collection_name: str):
        return self.__session.get_database(db_name).get_collection(collection_name)

    def get_all_data(self, db_name: str, collection_name: str):
        return list(self.__session.get_database(db_name).get_collection(collection_name).find())

    def get_one_column_data(self, db_name: str, collection_name: str, column_name: str):
        all_dicts = list(self.__session.get_database(db_name).get_collection(collection_name).find())
        return list(map(lambda o: o[column_name], all_dicts))

    def get_high_school_names(self):
        return self.get_one_column_data('tools_db', 'chinese_high_schools', 'school_name')


