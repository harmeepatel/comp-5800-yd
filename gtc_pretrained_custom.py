# from transformers import (
#     AutoConfig,
#     AutoModelForSeq2SeqLM,
#     AutoTokenizer,
#     MBart50Tokenizer,
#     MBart50TokenizerFast,
#     MBartTokenizer,
#     MBartTokenizerFast,
# )
# MULTILINGUAL_TOKENIZERS = [MBartTokenizer, MBartTokenizerFast, MBart50Tokenizer, MBart50TokenizerFast]
#
# tokenizer = AutoTokenizer.from_pretrained("./sp/models/bart-base-en-mix/")
# config = AutoConfig.from_pretrained("./sp/models/bart-base-en-mix/")
# model = AutoModelForSeq2SeqLM.from_config(config)
# # model = AutoModelForSeq2SeqLM.from_pretrained(
# #     "./sp/models/bart-base-en-mix",
# #     config="./sp/models/bart-base-en-mix/config.json",
# # )
# if isinstance(tokenizer, tuple(MULTILINGUAL_TOKENIZERS)):
#     print("tokenizer")
# a = model.resize_token_embeddings(len(tokenizer))
# print(a)
# print(model.config)

from transformers import BartTokenizer, BartForConditionalGeneration
ARTICLE_TO_SUMMARIZE = (
    "PG&E stated it scheduled the blackouts in response to forecasts for high winds "
    "amid dry conditions. The aim is to reduce the risk of wildfires. Nearly 800 thousand customers were "
    "scheduled to be affected by the shutoffs which were expected to last through at least midday tomorrow."
)

# from transformers import Trainer, TrainingArguments
# from transformers.modeling_bart import shift_tokens_right

tokenizer = BartTokenizer.from_pretrained('./sp/models/bart-base-en-mix/')
model = BartForConditionalGeneration.from_pretrained('./sp/models/bart-base-en-mix/')


inputs = tokenizer([ARTICLE_TO_SUMMARIZE], max_length=1024, return_tensors="pt")

# Generate Summary
summary_ids = model.generate(inputs["input_ids"], num_beams=2, min_length=0, max_length=20)
a = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

print(a)
# print(model.generate)

# def convert_to_features(example_batch):
#     input_encodings = tokenizer.batch_encode_plus(example_batch['text'], pad_to_max_length=True, max_length=1024, truncation=True)
#     target_encodings = tokenizer.batch_encode_plus(example_batch['summary'], pad_to_max_length=True, max_length=1024, truncation=True)
#
#     labels = target_encodings['input_ids']
#     decoder_input_ids = shift_tokens_right(labels, model.config.pad_token_id)
#     labels[labels[:, :] == model.config.pad_token_id] = -100
#
#     encodings = {
#         'input_ids': input_encodings['input_ids'],
#         'attention_mask': input_encodings['attention_mask'],
#         'decoder_input_ids': decoder_input_ids,
#         'labels': labels,
#     }
#
#     return encodings
#
#
# dataset = dataset.map(convert_to_features, batched=True)
# columns = ['input_ids', 'labels', 'decoder_input_ids', 'attention_mask',]
# dataset.set_format(type='torch', columns=columns)
#
# training_args = TrainingArguments(
#     output_dir='./models/bart-summarizer',
#     num_train_epochs=1,
#     per_device_train_batch_size=1,
#     per_device_eval_batch_size=1,
#     warmup_steps=500,
#     weight_decay=0.01,
#     logging_dir='./logs',
#
#
# )
#
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=dataset['train'],
#     eval_dataset=dataset['validation']
# )
