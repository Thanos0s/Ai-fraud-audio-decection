"""
Training Script for Audio Classifier
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import librosa
from pathlib import Path
from tqdm import tqdm
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.feature_extractor import AudioFeatureExtractor
from backend.models.audio_classifier import AudioClassifierNN


class AudioDataset(Dataset):
    """Custom dataset for audio files"""
    
    def __init__(self, audio_paths, labels, feature_extractor):
        self.audio_paths = audio_paths
        self.labels = labels
        self.feature_extractor = feature_extractor
    
    def __len__(self):
        return len(self.audio_paths)
    
    def __getitem__(self, idx):
        audio_path = self.audio_paths[idx]
        label = self.labels[idx]
        
        # Load and process audio
        try:
            audio, sr = librosa.load(audio_path, sr=16000)
            features = self.feature_extractor.extract_features(audio)
        except Exception as e:
            print(f"Error loading {audio_path}: {e}")
            features = np.zeros(200)  # Fallback
        
        return torch.FloatTensor(features), torch.LongTensor([label])


def prepare_dataset():
    """Load all audio files and create dataset"""
    base_path = Path('data/train')
    feature_extractor = AudioFeatureExtractor()
    
    audio_paths = []
    labels = []
    
    # AI-generated samples (label = 0)
    ai_path = base_path / 'ai_generated'
    if ai_path.exists():
        for lang_dir in ai_path.iterdir():
            if lang_dir.is_dir():
                for audio_file in list(lang_dir.glob('*.mp3')) + list(lang_dir.glob('*.wav')):
                    audio_paths.append(str(audio_file))
                    labels.append(0)
    
    # Human samples (label = 1)
    human_path = base_path / 'human'
    if human_path.exists():
        for lang_dir in human_path.iterdir():
            if lang_dir.is_dir():
                for audio_file in list(lang_dir.glob('*.mp3')) + list(lang_dir.glob('*.wav')):
                    audio_paths.append(str(audio_file))
                    labels.append(1)
    
    print(f"Total samples: {len(audio_paths)}")
    print(f"AI samples: {sum(1 for l in labels if l == 0)}")
    print(f"Human samples: {sum(1 for l in labels if l == 1)}")
    
    if len(audio_paths) == 0:
        print("\nWarning: No training data found!")
        print("Please add audio files to:")
        print("  - data/train/ai_generated/<language>/")
        print("  - data/train/human/<language>/")
        return None, None, None
    
    return audio_paths, labels, feature_extractor


def train_model():
    """Main training function"""
    print("Starting model training...\n")
    
    # Prepare data
    result = prepare_dataset()
    if result[0] is None:
        return
    
    audio_paths, labels, feature_extractor = result
    
    # Split dataset
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        audio_paths, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Create datasets
    train_dataset = AudioDataset(train_paths, train_labels, feature_extractor)
    val_dataset = AudioDataset(val_paths, val_labels, feature_extractor)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    
    # Get input size from first sample
    sample_features, _ = train_dataset[0]
    input_size = sample_features.shape[0]
    print(f"Feature vector size: {input_size}\n")
    
    # Initialize model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}\n")
    
    model = AudioClassifierNN(input_size).to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', patience=5
    )
    
    # Training loop
    num_epochs = 50
    best_val_loss = float('inf')
    
    print("Training started...\n")
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        
        for features, labels_batch in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}'):
            features = features.to(device)
            labels_batch = labels_batch.squeeze().to(device)
            
            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_correct += (predicted == labels_batch).sum().item()
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        
        with torch.no_grad():
            for features, labels_batch in val_loader:
                features = features.to(device)
                labels_batch = labels_batch.squeeze().to(device)
                
                outputs = model(features)
                loss = criterion(outputs, labels_batch)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_correct += (predicted == labels_batch).sum().item()
        
        # Calculate metrics
        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        train_acc = 100 * train_correct / len(train_dataset)
        val_acc = 100 * val_correct / len(val_dataset)
        
        print(f'\nEpoch {epoch+1}:')
        print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
        print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            Path('models').mkdir(exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'input_size': input_size,
                'val_loss': val_loss,
                'val_acc': val_acc
            }, 'models/best_model.pt')
            print('[OK] Model saved!')
        
        scheduler.step(val_loss)
    
    print('\nTraining complete!')
    print(f'Best validation accuracy: {val_acc:.2f}%')


if __name__ == '__main__':
    train_model()
