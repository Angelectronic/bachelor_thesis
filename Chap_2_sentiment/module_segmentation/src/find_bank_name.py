import re
from src.SQL_query import sql_operation


class bank_name:
    def __init__(self):
        select_query = sql_operation()
        self.select_ngan_hang = select_query.get_info("NGAN_HANG")

    def check_specific_bank(self, name, text):
        text = text.lower()
        specific_bank = self.select_ngan_hang.loc[self.select_ngan_hang["Ten"] == name]
        name_variations = specific_bank["Ten_viettat"].values[0] + "," + specific_bank["Ten_khac"].values[0]
        name_variations = name_variations.split(",")
        for item in name_variations:
            item = item.strip().lower()
            if re.search(r'\b' + item + r'\b', text):
                return True
            else:
                continue
        return False

    def check_bank_name(self, text):
        ngan_hang_name = []
        text = text.lower()

        # Kiểm tra xem đoạn văn bản có chứa bất kỳ giá trị nào trong cột "Ten", "Ten_viettat", hoặc "Ten_khac" hay không
        for index, row in self.select_ngan_hang.iterrows():
            if row["Ten_viettat"] is None:
                ngan_hang = row["Ten_khac"]
            elif row["Ten_khac"] is None:
                ngan_hang = row["Ten_viettat"]
            else:
                ngan_hang = row["Ten_viettat"] + "," + row["Ten_khac"]

            lst_ngan_hang = ngan_hang.split(",")

            for item in lst_ngan_hang:
                item = item.strip().lower()
                if item == 'ngân hàng tmcp sài gòn':
                    continue
                elif re.search(r'\b' + item + r'\b', text):
                    ngan_hang_name.append(row["Ten"])

        # Kiểm tra xem đoạn văn bản có chứa giá trị "Ngân hàng TMCP Sài Gòn" thật không?
        if 'Ngân hàng TMCP Sài Gòn' not in ngan_hang_name and re.search(r'\bngân hàng tmcp sài gòn\b(?! công| thương| -)\b', text):
            ngan_hang_name.append('Ngân hàng TMCP Sài Gòn')

        if ngan_hang_name == []:
            return False
        else:
            return ",".join(set(ngan_hang_name))
