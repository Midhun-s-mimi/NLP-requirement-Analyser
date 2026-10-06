import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityEngine:
    """
    Semantic similarity engine using the Sentence-Transformer model
    'all-MiniLM-L6-v2', loaded directly via HuggingFace Transformers.
    Replicates sentence-transformers' mean-pooling + L2 normalization exactly.
    Chosen to eliminate the pyarrow/datasets dependency chain, which is
    blocked by this machine's Application Control policy.
    """

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Loading similarity model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        print("✅ Similarity model loaded.")

    def _mean_pooling(self, model_output, attention_mask: torch.Tensor) -> torch.Tensor:
        token_embeddings = model_output[0]
        mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * mask_expanded, 1) / torch.clamp(mask_expanded.sum(1), min=1e-9)

    def encode(self, texts: list) -> np.ndarray:
        encoded = self.tokenizer(
            texts, padding=True, truncation=True, max_length=256, return_tensors="pt"
        )
        with torch.no_grad():
            output = self.model(**encoded)
        embeddings = self._mean_pooling(output, encoded["attention_mask"])
        embeddings = embeddings / embeddings.norm(p=2, dim=1, keepdim=True)  # L2 normalize
        return embeddings.numpy()

    def compute_batch_similarity(self, texts_a: list, texts_b: list) -> np.ndarray:
        """Cosine similarity between pairs (A[i] vs B[i])."""
        emb_a = self.encode(texts_a)
        emb_b = self.encode(texts_b)
        sim_matrix = cosine_similarity(emb_a, emb_b)
        return np.diag(sim_matrix)