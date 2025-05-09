# train_model.py
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch_geometric.data import Data, DataLoader, Dataset
from torch_geometric.nn import GATConv, global_mean_pool
from datasets import load_dataset

# Định nghĩa mô hình GATClassifier
class GATClassifier(nn.Module):
    def __init__(self, input_dim=256, hidden_dim=64, num_heads=4, dropout=0.2, num_classes=2):
        super(GATClassifier, self).__init__()
        self.gat1 = GATConv(
            in_channels=input_dim,
            out_channels=hidden_dim,
            heads=num_heads,
            dropout=dropout
        )
        self.gat2 = GATConv(
            in_channels=hidden_dim * num_heads,
            out_channels=hidden_dim,
            heads=1,
            dropout=dropout
        )
        self.fc = nn.Linear(hidden_dim, num_classes)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, data):
        x, edge_index, edge_weight, batch = data.x, data.edge_index, data.edge_attr, data.batch
        
        x = self.gat1(x, edge_index, edge_attr=edge_weight)
        x = F.elu(x)
        x = self.dropout(x)
        
        x = self.gat2(x, edge_index, edge_attr=edge_weight)
        x = F.elu(x)
        x = self.dropout(x)
        
        x = global_mean_pool(x, batch)
        x = self.fc(x)
        return x

# Load dữ liệu từ file JSON (Không chạy PCA nữa)
def load_processed_data(processed_file):
    """Load dataset đã được xử lý từ file JSON."""
    
    dataset = load_dataset('json', data_files=processed_file, split='train')
    dataset = dataset.train_test_split(test_size=0.2)
    
    train_dataset = MyOwnDataset(dataset=dataset['train'])
    val_dataset = MyOwnDataset(dataset=dataset['test'])

    print(f"Loaded dataset from {processed_file} - Train: {len(train_dataset)}, Val: {len(val_dataset)}")

    return train_dataset, val_dataset

# Hàm huấn luyện mô hình
def train_model(model, train_loader, val_loader, num_epochs=50, lr=0.001):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    best_val_acc = 0.0
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch in train_loader:
            print(f"Batch input shape before model: {batch.x.shape}")  # Kiểm tra số chiều input
            batch = batch.to(device)
            optimizer.zero_grad()
            out = model(batch)
            loss = criterion(out, batch.y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pred = out.argmax(dim=1)
            correct += (pred == batch.y).sum().item()
            total += batch.y.size(0)
        
        train_acc = correct / total
        
        # Đánh giá trên tập validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(device)
                out = model(batch)
                pred = out.argmax(dim=1)
                correct += (pred == batch.y).sum().item()
                total += batch.y.size(0)
        val_acc = correct / total
        
        print(f'Epoch {epoch+1}: Train Loss: {total_loss/len(train_loader):.4f}, '
              f'Train Acc: {train_acc:.4f}, Val Acc: {val_acc:.4f}')
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), 'best_model.pt')

class MyOwnDataset(Dataset):
    def __init__(self, root=None, transform=None, pre_transform=None, pre_filter=None, dataset=None):
        super().__init__(root, transform, pre_transform, pre_filter)
        self.dataset = dataset

    def len(self):
        return len(self.dataset)

    def get(self, idx):
        data = self.dataset[idx]
        return Data(
            x=torch.tensor(data['x'], dtype=torch.float),  # Dữ liệu đã có PCA
            edge_index=torch.tensor(data['edge_index'], dtype=torch.long),
            edge_attr=torch.tensor(data['edge_attr'], dtype=torch.float),
            y=torch.tensor(data['y'], dtype=torch.long)
        )

def main():
    processed_file = "./processed_dataset.json"  # File chứa dataset đã xử lý

    # Load dataset (Không cần chạy PCA nữa)
    train_dataset, val_dataset = load_processed_data(processed_file)

    # Tạo DataLoader
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    # Khởi tạo mô hình
    model = GATClassifier(
        input_dim=256,  # Cập nhật input_dim phù hợp với số chiều đã giảm bằng PCA
        hidden_dim=64,
        num_heads=4,
        dropout=0.2,
        num_classes=2
    )

    # Huấn luyện mô hình
    train_model(model, train_loader, val_loader)

if __name__ == "__main__":
    main()
