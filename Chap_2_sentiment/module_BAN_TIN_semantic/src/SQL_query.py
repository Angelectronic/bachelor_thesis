import sys
sys.path.append('..')
from connect_to_db.connect_db import connect_to_db
import pandas as pd
from datetime import datetime
import re

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
class sql_operation:
    # Khai báo biến kết nối tới CSDL
    def __init__(self):
        self.conn = connect_to_db()
        self.cursor = self.conn.cursor()

    # Hàm SELECT FROM TABEL
    def get_info(self, table, distinct_row = "", condition = None):
        if condition == None:
            if distinct_row != "":
                select_query = "SELECT DISTINCT {} FROM {}".format(distinct_row, table)
            else:
                select_query = "SELECT * FROM {}".format(table)
        else:
            if distinct_row != "":
                select_query = "SELECT DISTINCT {} FROM {} WHERE {}".format(distinct_row, table, condition)
            else:
                select_query = "SELECT * FROM {} WHERE {}".format(table, condition)
        print(select_query)
        try : 
            df = pd.read_sql(select_query, self.conn)
            
            return df
        except Exception as e:
            print(e)
            return False

    # Hàm INSERT
    def insert_to_db(self, table, columns, values, condition = None):
        str_value = ",".join(values)
        select_id_column_name = f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table}'"
        self.cursor.execute(select_id_column_name)
        columns_new = [column[3] for column in self.cursor.fetchall()]  # Lấy tên các cột từ kết quả truy vấn
        id_column = columns_new[0]  # Lấy tên cột đầu tiên
        
        id_table = ""
        if table == "BAN_TIN":
            str_date = values[1]
            str_date = str_date.strip("'")
            if str_date != "":
                date = datetime.strptime(str_date, "%Y-%m-%d")
                new_date = date.strftime("%d-%m-%Y")
                new_date = new_date.replace("-","_")
            else:
                new_date = datetime.now().date().strftime("%d-%m-%Y")
                new_date = new_date.replace("-","_")
                
            str_value = ",".join(values)
            
            source = re.search(r"'(.*?)'", values[0]).group(1)
            source_id = source_dictionary[source]
            
            select_id_query_1 = f"SELECT TOP 1 {id_column} FROM {table} ORDER BY CAST(RIGHT({id_column}, CHARINDEX('_', REVERSE({id_column})) - 1) AS INT) DESC" #revert giá trị cuối cùng của id_column sang dạng số để sắp xếp
            self.cursor.execute(select_id_query_1)
            try:
                last_id = self.cursor.fetchone()[0]
            except:
                last_id = False
                
            if last_id == False:
                id_ban_tin = new_date + "_" + source_id + "_" + "0"
            else:
                select_id_query_2 = f"SELECT * FROM {table} WHERE {id_column} = '{last_id}'"
                self.cursor.execute(select_id_query_2)
                last_record = self.cursor.fetchone()[0] # Lấy giá trị id_columns cuối cùng

                parts = last_record.split('_')
                last_value = int(parts[-1])
                new_last_value = last_value + 1
                parts[-1] = str(new_last_value)

                id_ban_tin = new_date + "_" + source_id + "_" + str(new_last_value)

            id_table = id_ban_tin
            if condition == None:
                insert_query = f"INSERT INTO {table} ({id_column},{columns}) VALUES ('{id_table}',{str_value})"
            else:
                insert_query = f"INSERT INTO {table} ({id_column},{columns}) VALUES ('{id_table}',{str_value}) {condition}"
            
            print(insert_query)    
            try : 
                self.conn.execute(insert_query)
                # nếu thành công thì tăng current_id lên 1
                # update table_id set id = id + 1 table_name= table 
                
                self.conn.commit()
                return True
            except Exception as e:
                print(e)
                return False
        else:
            select_id_query = f"SELECT TOP 1 {id_column} FROM {table} ORDER BY CAST({id_column} as INT) DESC"
            self.cursor.execute(select_id_query)
            try:
                last_record = self.cursor.fetchone()[0]  # Lấy bản ghi đầu tiên
            except Exception as e:
                last_record = False

            if last_record == False:
                id_table = '0'
            else:
                last_value = int(last_record)
                new_last_value = last_value + 1
                id_table = str(new_last_value)

            if condition == None:
                insert_query = f"INSERT INTO {table} ({id_column},{columns}) VALUES ('{id_table}',{str_value})"
            else:
                insert_query = f"INSERT INTO {table} ({id_column},{columns}) VALUES ('{id_table}',{str_value}) {condition}"
            
            print(insert_query)    
            try : 
                self.conn.execute(insert_query)
                # nếu thành công thì tăng current_id lên 1
                # update table_id set id = id + 1 table_name= table 
                
                self.conn.commit()
                return True
            except Exception as e:
                print(e)
                return False



    # Hàm UPDATE
    def update_to_db(self, table, set_condition, where_condition, condition = None):
        if condition == None:
            update_query = "UPDATE {} SET {} WHERE {}".format(table, set_condition, where_condition)
        else:
            update_query = "UPDATE {} SET {} WHERE {} {}".format(table, set_condition, where_condition, condition)
        print(update_query)
        try : 
            self.conn.execute(update_query)
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
 
    # Hàm DELETE
    def delete_to_db(self,table, where_condition, condition = None):
        if condition == None:
            delete_query = "DELETE FROM {} WHERE {}".format(table, where_condition)
        else:
            delete_query = "DELETE FROM {} WHERE {} {}".format(table, where_condition, condition)
        print(delete_query)
        try : 
            self.conn.execute(delete_query)
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
        
    def semantic_document(self):
        query = """
        SELECT 
            SAC_THAI.id_ban_tin,
            COUNT(CASE WHEN SAC_THAI.sac_thai = 'tích cực' THEN 1 END) AS tich_cuc,
            COUNT(CASE WHEN SAC_THAI.sac_thai = 'tiêu cực' THEN 1 END) AS tieu_cuc,
            COUNT(SAC_THAI.sac_thai) AS all_1,
            (COUNT(CASE WHEN SAC_THAI.sac_thai = 'tích cực' THEN 1 END) - 
            COUNT(CASE WHEN SAC_THAI.sac_thai = 'tiêu cực' THEN 1 END)) / 
            CAST(COUNT(SAC_THAI.sac_thai) AS FLOAT) AS semantic_score,
            CASE 
                WHEN (COUNT(CASE WHEN SAC_THAI.sac_thai = 'tích cực' THEN 1 END) - 
                    COUNT(CASE WHEN SAC_THAI.sac_thai = 'tiêu cực' THEN 1 END)) / 
                    CAST(COUNT(SAC_THAI.sac_thai) AS FLOAT) > 0 
                    THEN N'tích cực'
                WHEN (COUNT(CASE WHEN SAC_THAI.sac_thai = 'tích cực' THEN 1 END) - 
                    COUNT(CASE WHEN SAC_THAI.sac_thai = 'tiêu cực' THEN 1 END)) / 
                    CAST(COUNT(SAC_THAI.sac_thai) AS FLOAT) < 0 
                    THEN N'tiêu cực'
                ELSE N'trung lập'
            END AS semantic_label
        FROM SAC_THAI
        JOIN BAN_TIN ON BAN_TIN.id_ban_tin = SAC_THAI.id_ban_tin
        WHERE BAN_TIN.sac_thai_score = 0 AND SAC_THAI.sac_thai IS NOT NULL
        GROUP BY SAC_THAI.id_ban_tin;
        """
        try:
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            print(e)
            return False
        
    def semantic_document_new(self):
        query = """
        SELECT 
            SAC_THAI.id_ban_tin,
            COUNT(CASE WHEN tich_cuc > trung_lap AND tich_cuc > tieu_cuc THEN 1 END) AS tich_cuc,
            COUNT(CASE WHEN tieu_cuc > trung_lap AND tieu_cuc > tich_cuc THEN 1 END) AS tieu_cuc,
            COUNT(SAC_THAI.sac_thai) AS all_1,
            (COUNT(CASE WHEN tich_cuc > trung_lap AND tich_cuc > tieu_cuc THEN 1 END) - 
            COUNT(CASE WHEN tieu_cuc > trung_lap AND tieu_cuc > tich_cuc THEN 1 END)) / 
            CAST(COUNT(SAC_THAI.sac_thai) AS FLOAT) AS semantic_score,
            CASE 
                WHEN (COUNT(CASE WHEN tich_cuc > trung_lap AND tich_cuc > tieu_cuc THEN 1 END) - 
                    COUNT(CASE WHEN tieu_cuc > trung_lap AND tieu_cuc > tich_cuc THEN 1 END)) / 
                    CAST(COUNT(SAC_THAI.sac_thai) AS FLOAT) > 0 
                    THEN N'tích cực'
                WHEN (COUNT(CASE WHEN tich_cuc > trung_lap AND tich_cuc > tieu_cuc THEN 1 END) - 
                    COUNT(CASE WHEN tieu_cuc > trung_lap AND tieu_cuc > tich_cuc THEN 1 END)) / 
                    CAST(COUNT(SAC_THAI.sac_thai) AS FLOAT) < 0 
                    THEN N'tiêu cực'
                ELSE N'trung lập'
            END AS semantic_label
        FROM SAC_THAI
        JOIN BAN_TIN ON BAN_TIN.id_ban_tin = SAC_THAI.id_ban_tin
        WHERE BAN_TIN.sac_thai_score = 0 AND SAC_THAI.tich_cuc IS NOT NULL AND SAC_THAI.trung_lap IS NOT NULL AND SAC_THAI.tieu_cuc IS NOT NULL
        GROUP BY SAC_THAI.id_ban_tin;
        """
        try:
            df = pd.read_sql(query, self.conn)
            return df
        except Exception as e:
            print(e)
            return False
    
    # Hàm đóng kết nối
    def close_connection(self):
        try:
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            return False