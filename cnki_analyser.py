import db_tool
from collections import Counter
import env
import os
from tqdm import tqdm
from itertools import chain, combinations


def items_clean(item='', separator=''):
    return [p.replace(' ', '') for p in filter(lambda o: o, item.split(separator))]


class CNKIAnalyser:
    def __init__(self, collection_name, data_source):
        self.__db_helper = db_tool.MongoSessionHelper()
        self.__analysis_items = env.ANALYSIS_ITEMS
        self.__collection_name = collection_name
        self.__data_source = data_source

    def data_loader(self):
        if self.__collection_name in self.__db_helper.get_active_db('cnki_db').list_collection_names():
            in_opt = input('已存在集合{0}，是否重新加载？(Y/N)'.format(self.__collection_name))
            if in_opt == 'y' or in_opt == 'Y':
                self.__db_helper.get_active_collection('cnki_db', self.__collection_name).drop()
            elif in_opt == 'n' or in_opt == 'N':
                return
            else:
                print('输入错误，程序退出')
                exit(0)
        reader = open(self.__data_source, 'r', encoding='gbk')
        reader.readline()
        lines = reader.readlines()
        reader.close()
        bib_dicts = []
        for line in lines:
            items = line.split('\t')
            title = items[1]
            author_ori = items[2]
            if '"' in items[2]:
                author_ori = author_ori.replace('"', '')
                authors = items_clean(item=author_ori, separator=';')
            else:
                authors = items_clean(item=items[2], separator=';')
            authors = [o for o in map(lambda o: o.replace(' ', ''), authors)]
            organs = items_clean(item=items[3], separator=';')
            source = items[4]
            if ';;' in items[5]:
                keywords_ori = items[5].replace(';;', ';')
                keywords = items_clean(item=keywords_ori, separator=';')
            else:
                keywords = items_clean(item=items[5], separator=';')
            abstract = items[6]
            pub_time = items[7]
            funds = items_clean(item=items[9], separator=';;')
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
            if analysis_item == 'year':
                sorted_item_list = sorted(list(Counter(all_items).items()), key=lambda o: o[0], reverse=False)
            writer = open('{0}/{1}.csv'.format(output_dir, analysis_item), 'w+', encoding='gbk')
            for item in sorted_item_list:
                line = ','.join([item[0], str(item[1])]) + '\n'
                writer.write(line)
            writer.close()

    def output_wordcloud(self, output_dir):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        keywords_dicts = self.__db_helper.get_one_column_data('cnki_db', self.__collection_name, 'keywords')
        keywords_dicts = [o for o in keywords_dicts if o]
        all_keywords = list(sorted(chain.from_iterable(keywords_dicts)))
        keywords_in_line = ' '.join(all_keywords)
        keywords_in_line = keywords_in_line.replace(';', ' ')
        keywords_in_line = keywords_in_line.replace('"', '')
        print(keywords_in_line)

    def output_network(self, output_dir, network_name):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        item_dicts = self.__db_helper.get_one_column_data('cnki_db', self.__collection_name, network_name)
        item_dicts = [o for o in item_dicts if o]
        all_authors = list(sorted(chain.from_iterable(item_dicts)))
        all_authors_count = [o for o in Counter(all_authors).items()]
        all_authors_combs = []
        for item_dict in item_dicts:
            author_combs = [o for o in combinations(item_dict, 2)]
            if len(author_combs) == 0:
                continue
            for author_comb in author_combs:
                all_authors_combs.append(author_comb)
        all_authors_combs_count = [o for o in Counter(all_authors_combs).items()]
        with open('{0}/{1}_nodes.csv'.format(output_dir, network_name), 'w', encoding='utf-8') as f:
            f.write('Id,Label,Weight\n')
            lines = [','.join([o[0], o[0], str(o[1])]) + '\n' for o in all_authors_count]
            f.writelines(lines)

        with open('{0}/{1}_edges.csv'.format(output_dir, network_name), 'w', encoding='utf-8') as f:
            f.write('Source,Target,Weight\n')
            lines = [','.join([o[0][0], o[0][1], str(o[1])]) + '\n' for o in all_authors_combs_count]
            f.writelines(lines)
