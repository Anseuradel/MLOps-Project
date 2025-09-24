import torch 
from sklearn.model_selection import train_test_split 
from transformers import AutoTokenizer 
import config 
from src.model.data_extraction import load_data 
from src.model.data_processing import preprocess_data 
from src.model.dataloader import create_dataloader 
from src.model.model import SentimentClassifier 
from src.model.trainer import train_model 
from src.model.evaluate import evaluate_and_plot

def dataloader_train_test_val(df): 
    tokenizer = AutoTokenizer.from_pretrained(config.TOKENIZER_NAME) 
    data = create_dataloader(df, tokenizer, max_len=config.MAX_LEN, batch_size=config.BATCH_SIZE) 
    return data


def main():
    print("Loading dataset and tokenizer\n")

    # Load dataset
    data = load_data(config.DATASET_PATH, merge_labels=True)

    # Shuffle dataset
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)

    # Define chunk size (e.g., 1% of dataset)
    CHUNK_FRAC = 0.01
    chunk_size = int(len(data) * CHUNK_FRAC)

    # Initial model (fresh start)
    model = SentimentClassifier(n_classes=config.N_CLASSES).to(config.DEVICE)

    # Loop through chunks
    for i in range(0, len(data), chunk_size):
        print(f"\n⚡ Training on chunk {i//chunk_size + 1}\n")

        chunk = data.iloc[i:i+chunk_size]

        # Train/val/test split for this chunk
        train_data_raw, test_data_raw = train_test_split(chunk, test_size=config.TEST_SIZE, random_state=42)
        train_data, val_data = preprocess_data(train_data_raw, test_size=config.VAL_SIZE, max_length=config.MAX_LEN)

        train_data = dataloader_train_test_val(train_data)
        test_data = dataloader_train_test_val(test_data_raw)
        val_data = dataloader_train_test_val(val_data)

        # Train on this chunk (continue training same model)
        model = train_model(model, train_data, val_data, device=config.DEVICE, epochs=1)

        # Save checkpoint after each chunk
        torch.save(model.state_dict(), f"outputs/checkpoints/model_chunk_{i//chunk_size + 1}.pth")

    # Final evaluation after all chunks
    sentiment_mapper = (
        config.SENTIMENT_MAPPING if config.N_CLASSES == 5 else config.SENTIMENT_MAPPING_3_LABEL_VERSION
    )

    evaluate_and_plot(
        model,
        test_data,  # last test_data seen
        torch.nn.CrossEntropyLoss(),
        config.DEVICE,
        class_names=list(sentiment_mapper.values()),
        run_folder=config.MODEL_EVALUATION_OUTPUT_DIR,
    )
