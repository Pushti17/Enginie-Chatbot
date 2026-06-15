import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model

# 🔹 Check GPU
print("GPU Available:", torch.cuda.is_available())

# 🔹 Load dataset
with open("finetune_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dataset = Dataset.from_list(data)

# 🔹 Format dataset
def format_example(example):
    return {
        "text": f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
    }

dataset = dataset.map(format_example)

# 🔹 Model name
model_name = "mistralai/Mistral-7B-Instruct-v0.1"

# 🔹 Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# 🔹 4-bit Quantization (IMPORTANT)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# 🔹 Load model (LOW MEMORY SAFE)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

# 🔹 LoRA config
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# 🔹 Tokenization (FIXED WITH LABELS)
def tokenize(example):
    tokens = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

    # 🔥 CRITICAL FIX
    tokens["labels"] = tokens["input_ids"].copy()

    return tokens

dataset = dataset.map(tokenize, batched=True)

# 🔹 Training arguments (LOW GPU SAFE)
training_args = TrainingArguments(
    output_dir="./qlora-output",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=2,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
    optim="paged_adamw_8bit",
    report_to="none",
    no_cuda=False
)

# 🔹 Trainer
trainer = Trainer(
    model=model,
    train_dataset=dataset,
    args=training_args
)

# 🔹 Train
trainer.train()

# 🔹 Save adapter
model.save_pretrained("./qlora-finetuned")
tokenizer.save_pretrained("./qlora-finetuned")

print("✅ Training Complete!")