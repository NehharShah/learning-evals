"""
Advanced evaluation metrics for LLM performance assessment
Includes BLEU, ROUGE, and semantic similarity calculations
"""

import re
import math
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
import logging
from difflib import SequenceMatcher

try:
    import nltk
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize, sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. BLEU and ROUGE metrics will use fallback implementations.")

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Semantic similarity will use fallback implementation.")

logger = logging.getLogger(__name__)


def download_nltk_data():
    """Download required NLTK data for BLEU and ROUGE calculations"""
    if not NLTK_AVAILABLE:
        return False
    
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        return True
    except Exception as e:
        logger.error(f"Failed to download NLTK data: {e}")
        return False


def preprocess_text(text: str) -> str:
    """
    Preprocess text for evaluation metrics
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove punctuation (optional - can be configurable)
    # text = re.sub(r'[^\w\s]', '', text)
    
    return text.strip()


def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text into words
    
    Args:
        text: Input text
        
    Returns:
        List of tokens
    """
    if not text:
        return []
    
    if NLTK_AVAILABLE:
        try:
            return word_tokenize(preprocess_text(text))
        except Exception:
            # Fallback to simple tokenization
            pass
    
    # Simple tokenization fallback
    return preprocess_text(text).split()


def calculate_bleu_score(reference: str, candidate: str, weights: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)) -> float:
    """
    Calculate BLEU score for text similarity
    
    Args:
        reference: Reference text
        candidate: Candidate text
        weights: Weights for n-gram precision (default: equal weights for 1-4 grams)
        
    Returns:
        BLEU score (0-1, higher is better)
    """
    if not reference or not candidate:
        return 0.0
    
    try:
        # Tokenize texts
        reference_tokens = tokenize_text(reference)
        candidate_tokens = tokenize_text(candidate)
        
        if not reference_tokens or not candidate_tokens:
            return 0.0
        
        if NLTK_AVAILABLE:
            # Use NLTK's BLEU implementation
            smoothing = SmoothingFunction().method1
            score = sentence_bleu([reference_tokens], candidate_tokens, weights=weights, smoothing_function=smoothing)
            return float(score)
        else:
            # Fallback BLEU implementation
            return _calculate_bleu_fallback(reference_tokens, candidate_tokens, weights)
            
    except Exception as e:
        logger.error(f"Error calculating BLEU score: {e}")
        return 0.0


def _calculate_bleu_fallback(reference_tokens: List[str], candidate_tokens: List[str], weights: Tuple[float, ...]) -> float:
    """
    Fallback BLEU implementation without NLTK
    
    Args:
        reference_tokens: Tokenized reference text
        candidate_tokens: Tokenized candidate text
        weights: N-gram weights
        
    Returns:
        BLEU score
    """
    if not reference_tokens or not candidate_tokens:
        return 0.0
    
    # Calculate n-gram precisions
    precisions = []
    for n in range(1, len(weights) + 1):
        if len(candidate_tokens) < n:
            precisions.append(0.0)
            continue
        
        # Get n-grams
        candidate_ngrams = list(zip(*[candidate_tokens[i:] for i in range(n)]))
        reference_ngrams = list(zip(*[reference_tokens[i:] for i in range(n)]))
        
        if not candidate_ngrams:
            precisions.append(0.0)
            continue
        
        # Count matches
        matches = 0
        for ngram in candidate_ngrams:
            if ngram in reference_ngrams:
                matches += 1
        
        precision = matches / len(candidate_ngrams) if candidate_ngrams else 0.0
        precisions.append(precision)
    
    # Calculate geometric mean of precisions
    if not precisions or all(p == 0 for p in precisions):
        return 0.0
    
    log_precisions = [math.log(p) if p > 0 else float('-inf') for p in precisions]
    avg_log_precision = sum(log_precisions) / len(log_precisions)
    
    # Calculate brevity penalty
    if len(candidate_tokens) < len(reference_tokens):
        bp = math.exp(1 - len(reference_tokens) / len(candidate_tokens))
    else:
        bp = 1.0
    
    return bp * math.exp(avg_log_precision)


def calculate_rouge_score(reference: str, candidate: str, rouge_type: str = "rouge-1") -> Dict[str, float]:
    """
    Calculate ROUGE score for text similarity
    
    Args:
        reference: Reference text
        candidate: Candidate text
        rouge_type: Type of ROUGE (rouge-1, rouge-2, rouge-l)
        
    Returns:
        Dictionary with precision, recall, and f1 scores
    """
    if not reference or not candidate:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    try:
        # Tokenize texts
        reference_tokens = tokenize_text(reference)
        candidate_tokens = tokenize_text(candidate)
        
        if not reference_tokens or not candidate_tokens:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
        if rouge_type == "rouge-1":
            return _calculate_rouge_n(reference_tokens, candidate_tokens, n=1)
        elif rouge_type == "rouge-2":
            return _calculate_rouge_n(reference_tokens, candidate_tokens, n=2)
        elif rouge_type == "rouge-l":
            return _calculate_rouge_l(reference_tokens, candidate_tokens)
        else:
            logger.warning(f"Unknown ROUGE type: {rouge_type}")
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
            
    except Exception as e:
        logger.error(f"Error calculating ROUGE score: {e}")
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}


def _calculate_rouge_n(reference_tokens: List[str], candidate_tokens: List[str], n: int) -> Dict[str, float]:
    """
    Calculate ROUGE-N score
    
    Args:
        reference_tokens: Tokenized reference text
        candidate_tokens: Tokenized candidate text
        n: N-gram size
        
    Returns:
        ROUGE-N scores
    """
    if len(reference_tokens) < n or len(candidate_tokens) < n:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    # Get n-grams
    reference_ngrams = list(zip(*[reference_tokens[i:] for i in range(n)]))
    candidate_ngrams = list(zip(*[candidate_tokens[i:] for i in range(n)]))
    
    if not reference_ngrams or not candidate_ngrams:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    # Count matches
    reference_ngram_counts = Counter(reference_ngrams)
    candidate_ngram_counts = Counter(candidate_ngrams)
    
    matches = 0
    for ngram, count in candidate_ngram_counts.items():
        matches += min(count, reference_ngram_counts.get(ngram, 0))
    
    # Calculate precision and recall
    precision = matches / len(candidate_ngrams) if candidate_ngrams else 0.0
    recall = matches / len(reference_ngrams) if reference_ngrams else 0.0
    
    # Calculate F1
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }


def _calculate_rouge_l(reference_tokens: List[str], candidate_tokens: List[str]) -> Dict[str, float]:
    """
    Calculate ROUGE-L score (longest common subsequence)
    
    Args:
        reference_tokens: Tokenized reference text
        candidate_tokens: Tokenized candidate text
        
    Returns:
        ROUGE-L scores
    """
    if not reference_tokens or not candidate_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    # Calculate LCS length
    lcs_length = _longest_common_subsequence(reference_tokens, candidate_tokens)
    
    # Calculate precision and recall
    precision = lcs_length / len(candidate_tokens) if candidate_tokens else 0.0
    recall = lcs_length / len(reference_tokens) if reference_tokens else 0.0
    
    # Calculate F1
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }


def _longest_common_subsequence(seq1: List[str], seq2: List[str]) -> int:
    """
    Calculate the length of the longest common subsequence
    
    Args:
        seq1: First sequence
        seq2: Second sequence
        
    Returns:
        Length of LCS
    """
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]


def calculate_semantic_similarity(reference: str, candidate: str, method: str = "tfidf") -> float:
    """
    Calculate semantic similarity between texts
    
    Args:
        reference: Reference text
        candidate: Candidate text
        method: Similarity method (tfidf, jaccard, sequence)
        
    Returns:
        Similarity score (0-1, higher is more similar)
    """
    if not reference or not candidate:
        return 0.0
    
    try:
        if method == "tfidf" and SKLEARN_AVAILABLE:
            return _calculate_tfidf_similarity(reference, candidate)
        elif method == "jaccard":
            return _calculate_jaccard_similarity(reference, candidate)
        elif method == "sequence":
            return _calculate_sequence_similarity(reference, candidate)
        else:
            # Fallback to sequence similarity
            return _calculate_sequence_similarity(reference, candidate)
            
    except Exception as e:
        logger.error(f"Error calculating semantic similarity: {e}")
        return 0.0


def _calculate_tfidf_similarity(reference: str, candidate: str) -> float:
    """
    Calculate TF-IDF cosine similarity
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        Similarity score
    """
    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
        # Fit and transform both texts
        tfidf_matrix = vectorizer.fit_transform([reference, candidate])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    except Exception as e:
        logger.error(f"Error in TF-IDF similarity: {e}")
        return 0.0


def _calculate_jaccard_similarity(reference: str, candidate: str) -> float:
    """
    Calculate Jaccard similarity
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        Similarity score
    """
    # Tokenize and create sets
    reference_tokens = set(tokenize_text(reference))
    candidate_tokens = set(tokenize_text(candidate))
    
    if not reference_tokens or not candidate_tokens:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(reference_tokens.intersection(candidate_tokens))
    union = len(reference_tokens.union(candidate_tokens))
    
    return intersection / union if union > 0 else 0.0


def _calculate_sequence_similarity(reference: str, candidate: str) -> float:
    """
    Calculate sequence similarity using difflib
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        Similarity score
    """
    return SequenceMatcher(None, reference, candidate).ratio()


def calculate_advanced_metrics(reference: str, candidate: str) -> Dict[str, Any]:
    """
    Calculate all advanced evaluation metrics
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        Dictionary with all advanced metrics
    """
    if not reference or not candidate:
        return {
            "bleu_score": 0.0,
            "rouge_scores": {
                "rouge-1": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
                "rouge-2": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
                "rouge-l": {"precision": 0.0, "recall": 0.0, "f1": 0.0}
            },
            "semantic_similarity": {
                "tfidf": 0.0,
                "jaccard": 0.0,
                "sequence": 0.0
            }
        }
    
    try:
        # Calculate BLEU score
        bleu_score = calculate_bleu_score(reference, candidate)
        
        # Calculate ROUGE scores
        rouge_scores = {
            "rouge-1": calculate_rouge_score(reference, candidate, "rouge-1"),
            "rouge-2": calculate_rouge_score(reference, candidate, "rouge-2"),
            "rouge-l": calculate_rouge_score(reference, candidate, "rouge-l")
        }
        
        # Calculate semantic similarity
        semantic_similarity = {
            "tfidf": calculate_semantic_similarity(reference, candidate, "tfidf"),
            "jaccard": calculate_semantic_similarity(reference, candidate, "jaccard"),
            "sequence": calculate_semantic_similarity(reference, candidate, "sequence")
        }
        
        return {
            "bleu_score": bleu_score,
            "rouge_scores": rouge_scores,
            "semantic_similarity": semantic_similarity
        }
        
    except Exception as e:
        logger.error(f"Error calculating advanced metrics: {e}")
        return {
            "bleu_score": 0.0,
            "rouge_scores": {
                "rouge-1": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
                "rouge-2": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
                "rouge-l": {"precision": 0.0, "recall": 0.0, "f1": 0.0}
            },
            "semantic_similarity": {
                "tfidf": 0.0,
                "jaccard": 0.0,
                "sequence": 0.0
            }
        }


# Initialize NLTK data on module import
if NLTK_AVAILABLE:
    download_nltk_data() 