<h1>Semantic module</h1>
Sử dụng LLM (Viet-Mistral):<br>

```
from llm_semantic import init_model_normal, init_model_unsloth, predict_semantic

model, tokenizer = init_model_normal()
# model, tokenizer = init_model_unsloth()  # if use unsloth model
predict_semantic("Không chỉ duy trì thành công mức tăng trưởng tín dụng cao hơn bình quân toàn ngành, trong năm tài chính 2023 vừa qua, BVBank chuyển dịch thành công cấu trúc khách hàng. Nếu như trước đây, BVBank tập trung vào tệp khách hàng doanh nghiệp vừa và nhỏ thì trong năm 2023, ngân hàng đã chinh phục được tệp khách hàng cá nhân rộng lớn", model, tokenizer)
Đầu ra: "tích cực"
```

Sử dụng PhoBERT:<br>

```
from phobert_semantic import init_model, predict_semantic

model, tokenizer, segmenter = init_model()
predict_semantic('Không chỉ duy trì thành công mức tăng trưởng tín dụng cao hơn bình quân toàn ngành, trong năm tài chính 2023 vừa qua, BVBank chuyển dịch thành công cấu trúc khách hàng. Nếu như trước đây, BVBank tập trung vào tệp khách hàng doanh nghiệp vừa và nhỏ thì trong năm 2023, ngân hàng đã chinh phục được tệp khách hàng cá nhân rộng lớn', model, tokenizer, segmenter)
Đầu ra: "tích cực"
```