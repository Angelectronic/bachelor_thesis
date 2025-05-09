import torch
from transformers import AutoTokenizer, RobertaForSequenceClassification
from python_rdrsegmenter import load_segmenter 
from src.SQL_query import sql_operation

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def init_model():
    model = RobertaForSequenceClassification.from_pretrained("wonrax/phobert-base-vietnamese-sentiment").to(device)
    tokenizer = AutoTokenizer.from_pretrained("wonrax/phobert-base-vietnamese-sentiment", use_fast=False, truncation=True)
    segmenter = load_segmenter()

    return model, tokenizer, segmenter

def predict_semantic(text, model, tokenizer, segmenter):
    semanctic = ['tiêu cực', 'tích cực', 'trung lập']
    text = segmenter.tokenize(text.strip())
    inputs_ids = torch.tensor([tokenizer.encode(text, max_length=256)]).to(device)

    with torch.no_grad():
        outputs = model(inputs_ids)
        outputs = outputs.logits.softmax(dim=1).squeeze().cpu().numpy()
        predicted_class = semanctic[outputs.argmax()]
    return (outputs, predicted_class)

if __name__ == "__main__":
    SQL_query = sql_operation()
    batch_generator = SQL_query.get_info("SAC_THAI",distinct_row = "", condition = "sac_thai is NULL")

    model, tokenizer, segmenter = init_model()

    for i, sac_thai_null in enumerate(batch_generator):

        selected_sac_thai_null = sac_thai_null[["id_paragraph", "text_paragraph"]]

        for i in selected_sac_thai_null.iterrows():
            id_paragraph = i[1]["id_paragraph"]
            text = i[1]["text_paragraph"]
            outputs, sac_thai = predict_semantic(text, model, tokenizer, segmenter)
            sac_thai = sac_thai.strip()
            try:
                update = SQL_query.update_to_db('SAC_THAI', f"sac_thai = N'{sac_thai}'", f"id_paragraph = {id_paragraph}")
                update_tich_cuc = SQL_query.update_to_db('SAC_THAI', f"tich_cuc = {outputs[1]}", f"id_paragraph = {id_paragraph}")
                update_trung_lap = SQL_query.update_to_db('SAC_THAI', f"trung_lap = {outputs[2]}", f"id_paragraph = {id_paragraph}")
                update_tieu_cuc = SQL_query.update_to_db('SAC_THAI', f"tieu_cuc = {outputs[0]}", f"id_paragraph = {id_paragraph}")
            except Exception as e:
                print(e)
                continue

            # print(update)