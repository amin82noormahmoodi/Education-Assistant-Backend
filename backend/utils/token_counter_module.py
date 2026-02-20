from transformers import AutoTokenizer

class TokenCounter:
    def __init__(self, model_checkpoint: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    
    def count_tokens(self, text: str):
        tokens = self.tokenizer(
            text,
            return_tensors=None,
            add_special_tokens=True)["input_ids"]
        return len(tokens)