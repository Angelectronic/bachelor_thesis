from src.SQL_query import sql_operation

sql = sql_operation()
semantic = sql.semantic_document_new()
selected_semantic = semantic[["id_ban_tin","semantic_score","semantic_label"]]

for i in semantic.iterrows():
    id_ban_tin = i[1]["id_ban_tin"]
    semantic_score = i[1]["semantic_score"]
    semantic_label = i[1]["semantic_label"]

    sql.update_to_db("BAN_TIN", "sac_thai_score = {}, sac_thai = N'{}'".format(semantic_score, semantic_label), "id_ban_tin = '{}'".format(id_ban_tin))

sql.close_connection()