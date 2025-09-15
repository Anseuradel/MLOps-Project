from sklearn.model_selection import train_test_split

from config import *
from src.model.data_extraction import load_data
from src.model.data_processing import preprocess_data
from src.model.dataloader import create_dataloader
from src.model.model import SentimentClassifier

def datalaoder_train_test_val(df):
  data = create_dataloader(df, tokenizer,test_size=MAX_LEN, batch_size=BATCH_SIZE)
  return data

def main():
  # Step 1 : Data loading and tokenizer
  print("Loading dataset and tokenizer\n")

  # Load dataset using data_extraction file's function
  data = load_data(DATASET_PATH, merge_labels=True)

  # Data split before preprocessing
  train_data_raw, test_data_raw = train_test_split(data, test_size=TEST_SIZE, random_state = 42) 

  print("preprocesing dataset\n")
  # Apply preprocessing using data_processing file's fucntion
  train_data, val_data = preprocess_data(train_data_raw, test_size=VAL_SIZE, max_length= MAX_LEN)

  tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)

  # Step 2 : Dataloader
  print("Creating dataloaders\n") 
  # Creating dataloader using datalaoder file's function
   train_data = dataloader_train_test_val(train_data)
   test_data = datalaoder_train_test_val(test_data_raw)
   val_data = dataloader_train_test_val(val_data)

  #Step 3 : modeling
  # Initializing model
  print("Initializing model\n")
  model = SentimentClassifier(n_classes=N_CLASSES).to(DEVICE)

  # Training model
  print("Trainin model\n")

  
  
  
  
