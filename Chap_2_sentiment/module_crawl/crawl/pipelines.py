# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .settings import DRIVER_NAME, SERVER_NAME, DATABASE_NAME, PASSWORD, USERNAME, TABLE_NAME
import pyodbc as odbc
from scrapy import signals
from pydispatch import dispatcher
from connect_to_db.connect_db import connect_to_db

class CrawlPipeline(object):
    errors_url = []
    def __init__(self):
        self.conn = connect_to_db()
        self.cursor = self.conn.cursor()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def insert_to_db(self, table, data, condition = None):
        if condition == None:
            columns = "("
            values = "("
            
            try:
                data['time'] = data['time'].split(" - ")[0].strip()
                data['time'] = data['time'].split("/")
                data['time'] = data['time'][2] + "-" + data['time'][1] + "-" + data['time'][0]
            except:
                data['time'] = None
                self.errors_url.append(data['url'])
            
            for keys, value in data.items():
                if value == None:
                    continue
                columns = columns + keys + ", "
                value2 = value.replace("'", "''")
                values = values + 'N' + "'" + value2 + "', "
            columns = columns[:-2] + ")"
            values = values[:-2] + ")"
            insert_query = "INSERT INTO {} {} VALUES {}".format(table, columns, values)
        else:
            columns = "("
            values = "("
            for keys, value in data.items():
                columns = columns + keys + ", "
                value2 = value.replace("'", "''")
                values = values + 'N' + "'" + value2 + "', "
            columns = columns[:-2] + ")"
            values = values[:-2] + ")"
            condition = " WHERE " + condition
            insert_query = "INSERT INTO {} {} VALUES {} {}".format(table, columns, values, condition)
        try : 
            self.conn.execute(insert_query)
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def process_item(self, item, spider):
        data = dict(item)

        if self.insert_to_db(TABLE_NAME, data):
            print("Item added to SQL database!, url: ", item['url'])
        else:
            self.errors_url.append(item['url'])
            
    
    def close_connection(self):
        try:
            self.conn.close()
            return "Connection closed successfully!"
        except Exception as e:
            print(e)
            return "Failed to close connection!"

    def spider_closed(self, spider, reason):
        self.close_connection()
        print("Errors url: ", self.errors_url)