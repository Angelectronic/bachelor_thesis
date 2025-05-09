<h1>Hướng dẫn cài đặt, sử dụng các tính năng của hệ thống phân tích tin tức ngân hàng</h1>

Yêu cầu cài đặt trước
```sh
SQL Server 2022
python=3.8
```

Bước 1 : Clone dự án
```sh
git clone https://github.com/hieunguyenquoc/banking_project.git
```

Bước 1.5 : Update phiên bản mới nhất
```sh
git pull
```

Bước 2 : Cài đặt CSDL
```sh
Chạy file demo/database/banking_solution_version_1.sql trên SQL Server Management Studio
```

Bước 3 : Chạy tính năng crawl (Danh sách các spider: cafef, dantri, kinhtedothi, nhadautu, vietnambiz, vietnamnet vietstock, vneconomy, vnexpress)
```sh
cd ./module_crawl
scrapy crawl [ten_cac_spider]
```
(Có thể thay đổi DRIVER_NAME, DATABASE_NAME, SERVER_NAME, PASSWORD, USERNAME trong setting.py)

Bước 4 : Chạy tính năng import vào cơ cở dữ liệu từ file csv
```sh
cd ./module_import_csv_to_db
python insert_to_db_from_csv.py
```

Bước 5 : Chạy tính năng insert dữ liệu từ bảng BAN_TIN_CRAWL sang bảng BAN_TIN
```sh
cd ./module_insert_BAN_TIN_CRAWL_to_BAN_TIN
python insert_to_BAN_TIN.py
```

Bước 6 : Chạy tính năng tách đoạn và xác định ngân hàng, chủ đề cho đoạn đó
```sh
cd ./module_segmentation
python segmenter.py
```

Bước 7 : Chạy tính năng phân loại sắc thái tin
```sh
cd ./module_semantic
- Xác định sắc thái với PhoBERT
python phobert_semantic.py

- Xác định sắc thái với LLM - Vistral-7B-Chat
python llm_semantic.py
```

Bước 8 : Chạy semantic của cả BAN_TIN
```sh
cd ./module_BAN_TIN_semantic
python Main.py
```

Bước 9 : Chạy tính năng phân loại tin là kinh tế hay không
```sh
cd ./module_classification
python main.py
```

Bước 10 : Chạy giao diện
```sh
cd ./module_interface
python UI.py
```


