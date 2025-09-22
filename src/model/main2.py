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
  # Step 1 : Data loading and tokenizer
  print("Loading dataset and tokenizer\n")

  # Load dataset using data_extraction file's function
  data = load_data(config.DATASET_PATH, merge_labels=True)

  # ⚡ Reduce dataset temporarily for faster testing
  SMALL_FRAC = 0.5  # 1% of the dataset
  data = data.sample(frac=SMALL_FRAC, random_state=42).reset_index(drop=True)
  print(f"Using {len(data)} samples for quick testing.")


  # Data split before preprocessing
  train_data_raw, test_data_raw = train_test_split(data, test_size=config.TEST_SIZE, random_state = 42) 

  print("preprocesing dataset\n")
  # Apply preprocessing using data_processing file's fucntion
  train_data, val_data = preprocess_data(train_data_raw, test_size=config.VAL_SIZE, max_length=config.MAX_LEN)

  # tokenizer = AutoTokenizer.from_pretrained(config.TOKENIZER_NAME)

  # Step 2 : Dataloader
  print("Creating dataloaders\n") 
  # Creating dataloader using datalaoder file's function
  train_data = dataloader_train_test_val(train_data)
  test_data = dataloader_train_test_val(test_data_raw)
  val_data = dataloader_train_test_val(val_data)

  #Step 3 : modeling
  # Initializing model
  print("Initializing model\n")
  model = SentimentClassifier(n_classes=config.N_CLASSES).to(config.DEVICE)

  # Training model
  print("Training model\n")
  trained_model = train_model(model, train_data, val_data, device=config.DEVICE, epochs=config.EPOCHS)

  # Evaluate model 
  print("Evaluating model\n")

  sentiment_mapper = (
        config.SENTIMENT_MAPPING if config.N_CLASSES == 5 else config.SENTIMENT_MAPPING_3_LABEL_VERSION
    )

  evaluate_and_plot(
          trained_model,
          test_data,
          torch.nn.CrossEntropyLoss(),
          config.DEVICE,
          class_names=list(sentiment_mapper.values()),
          run_folder=config.MODEL_EVALUATION_OUTPUT_DIR,
      )


if __name__ == "__main__":
  main()
