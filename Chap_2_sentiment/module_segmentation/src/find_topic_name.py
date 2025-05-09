import re
from src.SQL_query import sql_operation


class topic_name:
    def __init__(self):
        select_query = sql_operation()
        self.select_topic = select_query.get_info("CHU_DE")

    def check_specific_topic(self, name, text):
        text = text.lower()
        specific_topic = self.select_topic.loc[self.select_topic["Ten"] == name]
        name_variations = specific_topic["Ten"].values[0] + "," + specific_topic["Dong_nghia"].values[0]
        name_variations = name_variations.split(",")
        for item in name_variations:
            item = item.strip().lower()
            if re.search(r'\b' + item + r'\b', text):
                return True
            else:
                continue
        return False

    def check_topic_name(self, text):
        topic_name = []
        text = text.lower()

        for index, row in self.select_topic.iterrows():
            if row['Ten'] is None:
                topics = row['Dong_nghia']
            elif row['Dong_nghia'] is None:
                topics = row['Ten']
            else:
                topics = row['Ten'] + "," + row['Dong_nghia']

            lst_topics = topics.split(",")

            for item in lst_topics:
                item = item.strip().lower()
                if re.search(r'\b' + item + r'\b', text):
                    topic_name.append(row['Ten'])

        if topic_name == []:
            return False
        else:
            return ",".join(set(topic_name))
