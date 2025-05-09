from src.SQL_query import sql_operation
import os

sql = sql_operation()

def convert_datetime_to_str(date):
    return date.strftime("%Y-%m-%d")
def ban_tin_export_to_csv(date=""):
    date_str = convert_datetime_to_str(date)
    sql_select = sql.get_info("BAN_TIN", condition=f"Ngay = '{date_str}'")
   
    if not os.path.exists("./data_csv"):    # create folder if not exist
        os.makedirs("./data_csv")
    csv_file = f"./data_csv/{date_str}.xlsx"
    # for index, row in sql_select.iterrows():
    #     id_ban_tin = row["id_ban_tin"]
    #     ban_tin_select = sql.get_info("BAN_TIN", condition=f"id_ban_tin='{id_ban_tin}'")
    #     # sql_select.loc[index,"title_ban_tin"] = ban_tin_select["title"]
    #     sql_select.loc[index,"url_ban_tin"] = ban_tin_select.iloc[0]["url"]
    sql_select.to_excel(csv_file, index=False)

    print("Done export")
    return csv_file

if __name__ == "__main__":
    print(ban_tin_export_to_csv("2024-01-05"))
