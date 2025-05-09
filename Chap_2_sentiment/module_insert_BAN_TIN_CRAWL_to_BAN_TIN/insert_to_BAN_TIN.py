from src.SQL_query import sql_operation
import hashlib
hash_object = hashlib.md5()

sql_query = sql_operation()
source_dictionary = {
    "cafef" : "00",
    "vnexpress" : "01",
    "vneconomy" : "02",
    "dantri" : "03",
    "vietnamnet" : "04",
    "vietstock" : "05",
    "kinhtedothi" : "06",
    "nhadautu" : "07",
    "vietnambiz" : "08",
}
SQL_query = sql_operation()
select_ban_tin_crawl = SQL_query.get_info("BAN_TIN_CRAWL",distinct_row = "", condition="url NOT IN (SELECT url FROM BAN_TIN)")
selected_ban_tin_crawl = select_ban_tin_crawl[["source","time","text","url"]]

for i in selected_ban_tin_crawl.iterrows():
    nguon = i[1]["source"]
    ngay = i[1]["time"]
    text = i[1]["text"]
    text = text.replace("'","''") if text else text
    url = i[1]["url"]
    hash_object.update(i[1]["url"].encode())
    url_hash = hash_object.hexdigest()
    try: 
        insert = sql_query.insert_to_db('BAN_TIN', "Nguon,Ngay,text,url,url_hash,sac_thai,sac_thai_score", (f"N'{nguon}'",f"'{ngay}'",f"N'{text}'",f"'{url}'",f"'{url_hash}'",f"N'trung lập'",f"0"))
    except Exception as e:
        print(e)
        continue
    print(insert)
    
    
    
    

