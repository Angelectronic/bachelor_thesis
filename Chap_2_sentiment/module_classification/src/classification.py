import pickle

class classification_binary:
    def __init__(self):
        self.model = pickle.load(open("./model/svm_version_1.pkl",'rb'))

    def predict(self, text):
        result = self.model.predict([text])
        return "".join(result)

# if __name__ == "__main__":
#     classify = classification_binary()
#     text = """
# Lợi nhuận Tesla giảm hơn một nửa
# Hôm 23/4, hãng xe điện Tesla (Mỹ) công bố báo cáo tài chính quý I, với các số liệu không đạt dự báo của giới phân tích.

# Lợi nhuận ròng của Tesla giảm 55% so với năm ngoái, về 1,13 tỷ USD. Doanh thu sụt 9%, còn 21,3 tỷ USD. Biên lợi nhuận mất 2%.

# Các mức giảm này thậm chí tệ hơn năm 2020 - thời điểm sản xuất của hãng bị gián đoạn vì Covid-19. Doanh thu mảng xe hơi co lại 13%, còn 17,38 tỷ USD.

# Dù vậy, hãng xe điện của tỷ phú Elon Musk trấn an nhà đầu tư rằng họ vẫn giữ kế hoạch làm xe giá rẻ. Mẫu này sẽ bắt đầu sản xuất vào nửa cuối 2025.

# Xe Model Y của Tesla trong nhà máy ở Gruenheide (Đức). Ảnh: Reuters
# Xe Model Y của Tesla trong nhà máy ở Gruenheide (Đức). Ảnh: Reuters

# Hãng xe điện Mỹ không tiết lộ nhiều thông tin về mẫu xe mới này, như mức giá mục tiêu hoặc số xe dự kiến sản xuất. Hãng và CEO Elon Musk cũng thường xuyên không theo kịp các hạn chót về ra mắt những mẫu xe trước. Tuy vậy, tuyên bố này vẫn khiến nhà đầu tư lạc quan, sau khi giới truyền thông đầu tháng này đưa tin hãng đã bỏ kế hoạch xe giá rẻ.

# Hôm qua, Musk cũng thông báo Tesla đầu tư vào cơ sở hạ tầng trí tuệ nhân tạo (AI). Ông tuyên bố công ty đang đàm phán với "một hãng xe lớn" để tích hợp công nghệ tự lái hoàn toàn (FSD) của hãng.

# Musk còn nói về tham vọng với robot hình người và công nghệ robotaxi. "Chúng tôi nên được coi là một công ty AI-robotics. Sai lầm khi coi Tesla chỉ là một hãng xe", ông khẳng định.

# Dù vậy, hãng xe điện này hôm qua một lần nữa cảnh báo triển vọng năm nay kém lạc quan. Họ cho biết "tăng trưởng doanh số bán xe năm nay có thể thấp hơn đáng kể so với năm ngoái".

# Cổ phiếu Tesla hôm qua tăng 11% trong phiên giao dịch ngoài giờ. Tuy nhiên, từ đầu năm, mã này giảm hơn 40% và có thời điểm thấp nhất kể từ tháng 1/2023. Nguyên nhân là nhà đầu tư lo ngại số xe giao được ít, cạnh tranh tại Trung Quốc tăng cao và hãng liên tiếp hạ giá sản phẩm.

# Đầu tháng này, hãng xe điện Mỹ cho biết số xe giao được giảm 8,5% trong quý I so với cùng kỳ năm ngoái. Quý cuối năm 2023, họ cũng để mất vị trí hãng ôtô điện lớn nhất thế giới về tay đối thủ Trung Quốc BYD.
# """
    
#     print(classify.predict(text))