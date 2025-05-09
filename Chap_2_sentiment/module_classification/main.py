from src.classification import classification_binary
from src.SQL_query import sql_operation
sql = sql_operation()

classify = classification_binary()
sql_select = sql.get_info("BAN_TIN_CRAWL")

for index, row in sql_select.iterrows():
    title = row["title"] if row["title"] is not None else " "
    summary = row["summary"] if row["summary"] is not None else " "
    text = row["text"] if row["text"] is not None else " "
    
    concatenate_txt = title + "\n" + summary + "\n" + text
    result = classify.predict(concatenate_txt)
    result_dict = {
        "text" : text,
        "class" : result
    }
    print(result_dict)
