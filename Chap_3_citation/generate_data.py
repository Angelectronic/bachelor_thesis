# generate_data.py
import os
import json
import torch
import numpy as np
import pickle
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from torch_geometric.data import Data

def load_json(filename):
    """Đọc dữ liệu từ file JSON."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def calc_sentence_sim(s1, s2):
    """Tính độ tương đồng giữa hai câu dựa trên từ chung."""
    s1 = s1.split()
    s2 = s2.split()
    if len(s1) == 0 or len(s2) == 0:
        return 0  # Tránh chia cho 0
    return len(set(s1) & set(s2)) / (np.log(len(s1) + 1) + np.log(len(s2) + 1))

def prepare_data(data_dir):
    graphs = []
    labels = []
    
    in_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.in')])
    in_files = in_files[0:10000]
    
    for idx, in_file in enumerate(in_files):
        print(f"Processing file {idx+1}/{len(in_files)}")  

        base_name = in_file.replace('.in', '')
        label_file = os.path.join(data_dir, f"{base_name}.label")

        if not os.path.exists(label_file):
            print(f"Warning: Missing label file for {in_file}, skipping...")
            continue

        in_data = load_json(os.path.join(data_dir, in_file))
        label_data = load_json(label_file)

        correct_citations = set(label_data["correct_citation"])
        citation_ids = in_data["citation_candidates"]

        try:
            embedding_sentences = load_json(f'./specter_embeddings_task1/{base_name}.json')["sentences"]
        except Exception as e:
            print(f"Warning: Error loading embeddings for {base_name}: {e}")
            continue

        for cid in citation_ids:
            label = 1 if cid in correct_citations else 0
            labels.append(label)

            try:
                candidate_vec = load_json(f"./candidates_storage_vec/{cid}.candidate")
            except FileNotFoundError:
                print(f"Warning: Missing file {cid}.candidate, skipping...")
                continue
            
            title_embedding = np.array(candidate_vec['title'])
            abstract_embeddings = np.array(candidate_vec['abstract'])

            nodes = np.vstack([embedding_sentences, title_embedding, abstract_embeddings])
            num_nodes = nodes.shape[0]

            similarity_matrix = cosine_similarity(nodes)

            edges = []
            edge_weights = []

            for i in range(num_nodes):
                for j in range(num_nodes):
                    if i != j:
                        edges.append([i, j])
                        text_sim = calc_sentence_sim("dummy_text_i", "dummy_text_j")  # Bỏ qua phần text để đơn giản
                        weight = [similarity_matrix[i, j], text_sim]
                        edge_weights.append(weight)

            graph_dict = {
                "nodes": nodes.astype(np.float32),
                "edges": np.array(edges, dtype=np.int64).T,
                "weights": np.array(edge_weights, dtype=np.float32)
            }
            graphs.append(graph_dict)

    return graphs, labels

def convert_to_pyg_format(graphs, labels):
    """Chuyển đổi danh sách graphs sang định dạng của PyTorch Geometric."""
    data_list = []
    for graph, label in zip(graphs, labels):
        x = torch.tensor(graph['nodes'], dtype=torch.float)
        edge_index = torch.tensor(graph['edges'], dtype=torch.long)
        edge_attr = torch.tensor(graph['weights'], dtype=torch.float)
        
        data = Data(
            x=x,
            edge_index=edge_index,
            edge_attr=edge_attr,
            y=torch.tensor([label], dtype=torch.long)
        )
        data_list.append(data)
    return data_list

def apply_pca_and_save(dataset, pca_dim=256, pca_model_path="pca_model.pkl"):
    """Chạy PCA trên toàn bộ dataset trước khi lưu vào file JSON."""
    
    all_embeddings = np.vstack([data["x"] for data in dataset])

    # Chạy PCA
    pca = PCA(n_components=pca_dim)
    transformed_embeddings = pca.fit_transform(all_embeddings)

    # Lưu PCA model để dùng lại sau này
    with open(pca_model_path, "wb") as f:
        pickle.dump(pca, f)

    print(f"PCA đã giảm từ {all_embeddings.shape[1]} xuống {pca_dim} chiều.")

    # Cập nhật dataset sau khi PCA
    index = 0
    for data in dataset:
        num_nodes = len(data["x"])
        data["x"] = transformed_embeddings[index: index + num_nodes].tolist()
        index += num_nodes

    return dataset

def process_and_save_data(data_dir, processed_file, pca_dim=256):
    """Xử lý dữ liệu thô, áp dụng PCA và lưu dataset đã xử lý vào file JSON."""
    
    graphs, labels = prepare_data(data_dir)  # Chuẩn bị dữ liệu gốc
    dataset = convert_to_pyg_format(graphs, labels)  # Chuyển đổi sang PyG dataset

    # Chuyển đổi PyG dataset thành JSON-compatible format
    dataset_json = []
    for data in dataset:
        dataset_json.append({
            "x": data.x.tolist(),
            "edge_index": data.edge_index.tolist(),
            "edge_attr": data.edge_attr.tolist(),
            "y": data.y.tolist(),
        })

    # Áp dụng PCA trước khi lưu
    dataset_json = apply_pca_and_save(dataset_json, pca_dim)

    # Lưu xuống file JSON
    with open(processed_file, "w") as f:
        json.dump(dataset_json, f)
    
    print(f"Processed dataset saved to {processed_file}")

def main():
    data_dir = "./data_train/task1"  # Thư mục chứa dữ liệu thô
    processed_file = "./processed_dataset.json"  # File để lưu dataset đã xử lý
    pca_dim = 256  # Số chiều sau PCA

    process_and_save_data(data_dir, processed_file, pca_dim)

if __name__ == "__main__":
    main()
