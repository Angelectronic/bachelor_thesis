import gradio as gr
from gradio_calendar import Calendar
from visualizer import visualizer
from src.export_to_file import export_to_csv
from src.insert_to_db_from_csv import insert_excel_to_db
from src.ban_tin_export_to_file import ban_tin_export_to_csv
def plot(bank, topic, date_start, date_end):
    fig = vis.display(bank, topic, date_start, date_end)
    return fig

def upload_csv(file):
    uploaded_file_path = file.name
    return uploaded_file_path

# def change_dropdown():
#     vis = visualizer()
#     vis.bank.append("Tất cả")
#     vis.topic.append("Tất cả")
#     return gr.Dropdown(value="Tất cả", label="Ngân hàng", choices=vis.bank), \
#            gr.Dropdown(value="Tất cả", label="Chủ đề", choices=vis.topic)

vis = visualizer()
vis.bank.append("Tất cả")
vis.topic.append("Tất cả")

with gr.Blocks() as demo:
    gr.HTML(
        """
        <div style="text-align: center;">
            <h1 style="font-weight: bold; font-size: 40px; color: #2E86C1; font-family: Arial, sans-serif;">
                Banking Sentiment Analysis Project
            </h1>
        </div>
        """
    )
    with gr.Tab("Thống kê & Xuất dữ liệu"):
        gr.Markdown(
            r"<h2>Banking Sentiment Analyzer</h1>"
        )
        gr.Markdown(
            r"<h3>1: Chọn ngân hàng và chủ đề (vui lòng chọn ít nhất 1 ngân hàng hoặc 1 chủ đề cụ thể)</h3>"
        )
        with gr.Row():
            with gr.Column():
                bank = gr.Dropdown(value="Tất cả", label="Ngân hàng", choices=vis.bank)
            with gr.Column():
                topic = gr.Dropdown(value="Tất cả", label="Chủ đề", choices=vis.topic)
        gr.Markdown(
            r"<h3>2: Chọn khoảng thời gian các bài viết được đăng tải</h3>"
        )
        with gr.Row():
            date_start = Calendar(
                value="2022-01-01",
                type="datetime",
                label="Từ ngày",
                info="Bấm vào biểu tượng lịch để chọn ngày hoặc nhập theo định dạng mm-dd-yyyy"
            )
            date_end = Calendar(
                value="2025-01-01",
                type="datetime",
                label="Đến ngày",
                info="Bấm vào biểu tượng lịch để chọn ngày hoặc nhập theo định dạng mm-dd-yyyy"
            )
        btn = gr.Button(value="Thống kê")
        with gr.Column():
            fig = gr.Plot()
        btn.click(
            plot,
            inputs=[bank, topic, date_start, date_end],
            outputs=fig
        )

        btn0 = gr.Button(value="Xuất ra file csv")
        csv_output = gr.File()
        btn0.click(
            export_to_csv,
            inputs=[bank, topic, date_start, date_end],
            outputs=csv_output
        )

    with gr.Tab("Thêm dữ liệu"):
        gr.Markdown(
            r"<h2>Thêm dữ liệu vào bảng</h2>"
        )
        with gr.Row():
            with gr.Column():
                table = gr.Dropdown(label="Bảng dữ liệu", choices=["Ngân hàng", "Chủ đề"])

        file_input = gr.File(label="Upload CSV", type="filepath")
        file_path_output = gr.Textbox(label="File Path")

        # Upload CSV và trả về đường dẫn file
        file_input.upload(upload_csv, inputs=file_input, outputs=file_path_output)
        result = gr.Textbox(label="Kết quả")
        # Gọi hàm insert_excel_to_db với cả hai input
        submit_btn = gr.Button("Insert to database")
        submit_btn.click(
            insert_excel_to_db,
            inputs=[table, file_path_output],
            outputs=result
        )
        # .then(
        #     change_dropdown, outputs=[bank, topic]
        # )
    with gr.Tab("Export dữ liệu theo ngày"):
        gr.Markdown(
            r"<h2>Export dữ liệu theo ngày</h2>"
        )
        with gr.Row():
            date = Calendar(
                value="2022-01-01",
                type="datetime",
                label="Ngày",
                info="Bấm vào biểu tượng lịch để chọn ngày hoặc nhập theo định dạng mm-dd-yyyy"
            )

        btn2 = gr.Button(value="Xuất ra file csv")
        csv_output0 = gr.File()
        btn2.click(
            ban_tin_export_to_csv,
            inputs=[date],
            outputs=csv_output0
        )
if __name__ == "__main__":
    demo.launch(share = True)
