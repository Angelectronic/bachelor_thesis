from src.SQL_query import sql_operation
import os

sql = sql_operation()

def convert_datetime_to_str(date):
    return date.strftime("%Y-%m-%d")
def export_to_csv(bank_name="Tất cả", topic="Tất cả", date_start="",date_end=""):

    date_start_str = convert_datetime_to_str(date_start)
    date_end_str = convert_datetime_to_str(date_end)
    if bank_name == "Tất cả" and topic == "Tất cả":
        sql_select = sql.get_info("SAC_THAI", condition=f"Ngay between '{date_start_str}'AND '{date_end_str}'")
    elif bank_name == "Không chứa ngân hàng":
        if topic == "Tất cả":
            sql_select = sql.get_info("SAC_THAI", condition=f"Ngay between '{date_start_str}'AND '{date_end_str}' AND ngan_hang is NULL")
        else:
            sql_select = sql.get_info("SAC_THAI", condition=f"Ngay between '{date_start_str}'AND '{date_end_str}' AND ngan_hang is NULL AND chu_de=N'{topic}'")

    else:
        if bank_name == "Tất cả":
            sql_select = sql.get_info("SAC_THAI", condition=f"Ngay between '{date_start_str}'AND '{date_end_str}' AND chu_de=N'{topic}'")
        elif topic == "Tất cả":
            sql_select = sql.get_info("SAC_THAI", condition=f"Ngay between '{date_start_str}'AND '{date_end_str}' AND ngan_hang=N'{bank_name}'")
        else:
            sql_select = sql.get_info("SAC_THAI", condition=f"Ngay between '{date_start_str}'AND '{date_end_str}' AND ngan_hang=N'{bank_name}' AND chu_de=N'{topic}'")

    if not os.path.exists("./data_csv"):    # create folder if not exist
        os.makedirs("./data_csv")
    csv_file = f"./data_csv/{bank_name}_{topic}_{date_start_str}_{date_end_str}.xlsx"
    for index, row in sql_select.iterrows():
        id_ban_tin = row["id_ban_tin"]
        ban_tin_select = sql.get_info("BAN_TIN", condition=f"id_ban_tin='{id_ban_tin}'")
        # sql_select.loc[index,"title_ban_tin"] = ban_tin_select["title"]
        sql_select.loc[index,"url_ban_tin"] = ban_tin_select.iloc[0]["url"]
    sql_select.to_excel(csv_file, index=False)

    print("Done export")
    return csv_file

# if __name__ == "__main__":
#     print(export_to_csv("Ngân hàng TMCP Đông Á","An toàn của hệ thống","2023-10-28","2024-01-05"))
