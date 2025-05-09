import torch
# from unsloth import FastLanguageModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from src.SQL_query import sql_operation


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# def init_model_unsloth():  # Supports NVIDIA GPUs since 2018+. Minimum CUDA Capability 7.0 (V100, T4, Titan V, RTX 20, 30, 40x, A100, H100, L40 etc) 
#     max_seq_length = 1024 
#     dtype = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
#     load_in_4bit = True # Use 4bit quantization to reduce memory usage. Can be False.

#     model, tokenizer = FastLanguageModel.from_pretrained(
#         model_name = "Viet-Mistral/Vistral-7B-Chat", 
#         max_seq_length = max_seq_length,
#         dtype = dtype,
#         load_in_4bit = load_in_4bit, 
#     )

#     tokenizer.pad_token = tokenizer.bos_token
#     model.config.pad_token_id = model.config.bos_token_id
#     tokenizer.padding_side = "right"

#     model = FastLanguageModel.get_peft_model(
#         model,
#         r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
#         target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
#                         "gate_proj", "up_proj", "down_proj",],
#         lora_alpha = 16,
#         lora_dropout = 0, # Supports any, but = 0 is optimized
#         bias = "none",    # Supports any, but = "none" is optimized
#         use_gradient_checkpointing = True,
#         random_state = 3407,
#         use_rslora = False,
#         loftq_config = None, 
#     )

#     FastLanguageModel.for_inference(model)
#     return model, tokenizer

def init_model_normal():
    quantization_config = BitsAndBytesConfig(load_in_4bit=True)

    tokenizer = AutoTokenizer.from_pretrained('Viet-Mistral/Vistral-7B-Chat')
    model = AutoModelForCausalLM.from_pretrained(
        'Viet-Mistral/Vistral-7B-Chat',
        torch_dtype=torch.float16, # change to torch.float16 if you're using V100
        device_map="auto",
        use_cache=True,
        quantization_config=quantization_config,
    )
    tokenizer.pad_token = tokenizer.bos_token
    model.config.pad_token_id = model.config.bos_token_id
    tokenizer.padding_side = "right"
    return model, tokenizer

def predict_semantic(text, model, tokenizer):
    semanctic = ['tích cực', 'trung lập', 'tiêu cực']

    system_prompt = "Phân loại quan điểm của văn bản về tài chính bên dưới thành 'tích cực', 'tiêu cực', hoặc 'trung lập', đồng thời cung cấp xác suất cho từng phân loại"
    conversation = [{"role": "system", "content": system_prompt },
                    {"role": "user", "content": "Không chỉ duy trì thành công mức tăng trưởng tín dụng cao hơn bình quân toàn ngành, trong năm tài chính 2023 vừa qua, BVBank chuyển dịch thành công cấu trúc khách hàng. Nếu như trước đây, BVBank tập trung vào tệp khách hàng doanh nghiệp vừa và nhỏ thì trong năm 2023, ngân hàng đã chinh phục được tệp khách hàng cá nhân rộng lớn"},
                    {"role": "assistant", "content": "tích cực: 0.97, trung lập:0.02, tiêu cực: 0.01"},
                    {"role": "user", "content": "CTCP Chứng khoán BIDV (BSC – mã BSI) vừa công bố phương án bán cổ phiếu quỹ thực hiện theo Nghị quyết HĐQT số 666/NQ-BSC ngày 29/9. Theo đó, BSC dự kiến sẽ bán toàn bộ cổ phiếu quỹ đang nắm giữ với số lượng 505.660 đơn vị (chiếm 0,25% vốn điều lệ)"},
                    {"role": "assistant", "content": "tích cực: 0.21, trung lập: 0.50, tiêu cực: 0.29"},
                    {"role": "user", "content": "Nhiều cổ đông ngân hàng Đông Á lo lắng với phương án thu hồi nợ của ngân hàng, một cổ đông cho rằng trường hợp rủi ro phía doanh nghiệp không huy động được nguồn vốn mục tiêu thì việc thu hồi nợ của ngân hàng có thể gặp khó khăn"},
                    {"role": "assistant", "content": "tích cực: 0.14, trung lập: 0.10, tiêu cực: 0.76"},
                    {"role": "user", "content": text},
                    ]

    input_ids = tokenizer.apply_chat_template(conversation, return_tensors="pt").to(model.device)

    out_ids = model.generate(
        input_ids=input_ids,
        max_new_tokens=50,
        do_sample=True,
        top_p=0.95,
        top_k=40,
        temperature=0.1,
        repetition_penalty=1.05,
        pad_token_id=tokenizer.eos_token_id,
    )
    preds = tokenizer.batch_decode(out_ids[:, input_ids.size(1): ], skip_special_tokens=True)[0].strip()
    preds = preds.split(",")
    outputs = [float(i.split(":")[1]) for i in preds]
    pred = semanctic[outputs.index(max(outputs))]
    return outputs, pred

if __name__ == "__main__":
    SQL_query = sql_operation()
    batch_generator = SQL_query.get_info("SAC_THAI",distinct_row = "", condition = "sac_thai is NULL")

    model, tokenizer = init_model_normal()
    for sac_thai_null in batch_generator:
        selected_sac_thai_null = sac_thai_null[["id_paragraph", "text_paragraph"]]

        for i in selected_sac_thai_null.iterrows():
            id_paragraph = i[1]["id_paragraph"]
            text = i[1]["text_paragraph"]
            outputs, sac_thai = predict_semantic(text, model, tokenizer)
            sac_thai = sac_thai.strip()
            try:
                update = SQL_query.update_to_db('SAC_THAI', f"sac_thai = N'{sac_thai}'", f"id_paragraph = {id_paragraph}")
                update_tich_cuc = SQL_query.update_to_db('SAC_THAI', f"tich_cuc = {outputs[0]}", f"id_paragraph = {id_paragraph}")
                update_trung_lap = SQL_query.update_to_db('SAC_THAI', f"trung_lap = {outputs[1]}", f"id_paragraph = {id_paragraph}")
                update_tieu_cuc = SQL_query.update_to_db('SAC_THAI', f"tieu_cuc = {outputs[2]}", f"id_paragraph = {id_paragraph}")
            except Exception as e:
                print(e)
                continue

            print(update)
            print(update_tich_cuc)
            print(update_trung_lap)
            print(update_tieu_cuc)
