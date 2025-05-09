import pandas as pd
from src.SQL_query import sql_operation

sql = sql_operation()

def insert_excel_to_db(table, data_path):
    tabel_ = ""
    if table == "Ngân hàng":
        tabel_ = "NGAN_HANG"
    else:
        tabel_ = "CHU_DE"
    excel_type = data_path.split(".")[-1]
    if excel_type == "csv":
        data = pd.read_csv(data_path,encoding="utf-8")
    elif excel_type == "xlsx":
        data = pd.read_excel(data_path)
    if tabel_ == "CHU_DE":
        try :
            for index, row in data.iterrows():
                Ten = row["Ten"]
                Dong_nghia = row["Dong_nghia"]
                Tich_cuc = row["Tich_cuc"]
                Tieu_cuc = row["Tieu_cuc"]
                # id_chu_de_con = row["id_chu_de_con"]
                
                insert = sql.insert_to_db(tabel_, "Ten,Dong_nghia,Tich_cuc,Tieu_cuc", (f"N'{Ten}'",f"N'{Dong_nghia}'",f"N'{Tich_cuc}'",f"N'{Tieu_cuc}'"))
            return "Import thành công vào chủ đề"
        except Exception as e:
            return e
    elif tabel_ == "NGAN_HANG":
        try :
            for index, row in data.iterrows():
                Ten = row["Ten"]
                Ten_viettat = row["Ten_viettat"]
                Ten_khac = row["Ten_khac"]
                
                insert = sql.insert_to_db(tabel_, "Ten,Ten_Viettat,Ten_khac", (f"N'{Ten}'",f"N'{Ten_viettat}'",f"N'{Ten_khac}'"))
            return "Import thành công vào ngân hàng"
        except Exception as e:
            return e
    
# if __name__ == "__main__":
#     table = "NGAN_HANG"
#     data_path = "data_test/test_insert_to_db_NGAN_HANG.xlsx"
#     print(insert_excel_to_db(table, data_path))
            
        
