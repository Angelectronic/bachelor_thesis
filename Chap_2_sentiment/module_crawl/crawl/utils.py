import sys
sys.path.append('..')
from connect_to_db.connect_db import connect_to_db

def already_scraped():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    urls = cursor.execute("SELECT url FROM BAN_TIN_CRAWL").fetchall()
    lists_item = []
    for item in urls:
        lists_item.append(item[0])
    
    origins = cursor.execute("SELECT origin FROM BAN_TIN_CRAWL").fetchall()
    for item in origins:
        lists_item.append(item[0])
    conn.close()
    return lists_item