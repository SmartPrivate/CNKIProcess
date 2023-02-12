import db_tool
from collections import Counter
import env
import os
from tqdm import tqdm


def items_clean(item='', seperator=''):
    return list(filter(lambda o: o, item.split(seperator)))


class CNKIAnalyser:
    def __init__(self, collection_name, data_source):
        self.__db_helper = db_tool.MongoSessionHelper()
        self.__analysis_items = env.ANALYSIS_ITEMS
        self.__collection_name = collection_name
        self.__data_source = data_source

    def data_loader(self):
        reader = open(self.__data_source, 'r', encoding='gbk')
        reader.readline()
        lines = reader.readlines()
        reader.close()
        bib_dicts = []
        for line in lines:
            items = line.split('\t')
            title = items[1]
            authors = items_clean(item=items[2], seperator=';')
            organs = items_clean(item=items[3], seperator=';')
            source = items[4]
            keywords = items_clean(item=items[5], seperator=';;')
            abstract = items[6]
            pub_time = items[7]
            funds = items_clean(item=items[9], seperator=';;')
            year = int(items[10])
            bib_dicts.append(dict(title=title, authors=authors, organs=organs, source=source, keywords=keywords, abstract=abstract, pub_time=pub_time, funds=funds, year=year))
        self.__db_helper.get_active_collection('cnki_db', self.__collection_name).insert_many(bib_dicts)
        self.organ_clean()

    def organ_clean(self):
        school_names = self.__db_helper.get_high_school_names()
        session = self.__db_helper.get_active_collection('cnki_db', self.__collection_name)
        all_dicts = self.__db_helper.get_all_data('cnki_db', self.__collection_name)
        for all_dict in all_dicts:
            _id = all_dict['_id']
            organs = all_dict['organs']
            new_organs = []
            for i in range(len(organs)):
                organ = organs[i]
                new_organs.append(organ)
                for school_name in school_names:
                    if school_name in organ:
                        new_organs[i] = school_name
                        break
            session.update_one({'_id': _id}, {'$set': {'organs': new_organs}})

    def output_stat_result(self, output_dir):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for analysis_item in self.__analysis_items:
            item_dicts = self.__db_helper.get_one_column_data('cnki_db', self.__collection_name, analysis_item)
            all_items = []
            for item_dict in item_dicts:
                if type(item_dict).__name__ == 'int':
                    item_dict = str(item_dict)
                if type(item_dict).__name__ == 'str':
                    item_dict = [item_dict]
                if len(item_dict) < 1:
                    continue
                all_items.extend(item_dict)
            sorted_item_list = sorted(list(Counter(all_items).items()), key=lambda o: o[1], reverse=True)
            writer = open('{0}/{1}.csv'.format(output_dir, analysis_item), 'w+', encoding='gbk')
            for item in sorted_item_list:
                line = ','.join([item[0], str(item[1])]) + '\n'
                writer.write(line)
            writer.close()
