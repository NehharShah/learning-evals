#!/usr/bin/env python3
"""
Test script for advanced evaluation metrics
Run this to verify BLEU, ROUGE, and semantic similarity calculations work correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import only the advanced metrics module directly to avoid config dependencies
try:
    from app.utils.advanced_metrics import (
        calculate_bleu_score,
        calculate_rouge_score,
        calculate_semantic_similarity,
        calculate_advanced_metrics
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the backend directory and have installed the requirements:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def test_advanced_metrics():
    """Test the advanced metrics with sample data"""
    
    print("🧪 Testing Advanced Evaluation Metrics")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Exact Match",
            "reference": "The capital of France is Paris.",
            "candidate": "The capital of France is Paris."
        },
        {
            "name": "Similar Meaning",
            "reference": "The capital of France is Paris.",
            "candidate": "Paris is the capital city of France."
        },
        {
            "name": "Partial Match",
            "reference": "The capital of France is Paris.",
            "candidate": "France's capital is Paris."
        },
        {
            "name": "Different Content",
            "reference": "The capital of France is Paris.",
            "candidate": "The weather is sunny today."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Reference: {test_case['reference']}")
        print(f"Candidate: {test_case['candidate']}")
        
        # Calculate individual metrics
        bleu = calculate_bleu_score(test_case['reference'], test_case['candidate'])
        rouge_1 = calculate_rouge_score(test_case['reference'], test_case['candidate'], 'rouge-1')
        rouge_2 = calculate_rouge_score(test_case['reference'], test_case['candidate'], 'rouge-2')
        rouge_l = calculate_rouge_score(test_case['reference'], test_case['candidate'], 'rouge-l')
        semantic_tfidf = calculate_semantic_similarity(test_case['reference'], test_case['candidate'], 'tfidf')
        semantic_jaccard = calculate_semantic_similarity(test_case['reference'], test_case['candidate'], 'jaccard')
        semantic_sequence = calculate_semantic_similarity(test_case['reference'], test_case['candidate'], 'sequence')
        
        # Calculate all metrics at once
        all_metrics = calculate_advanced_metrics(test_case['reference'], test_case['candidate'])
        
        print(f"  BLEU Score: {bleu:.3f}")
        print(f"  ROUGE-1 F1: {rouge_1['f1']:.3f}")
        print(f"  ROUGE-2 F1: {rouge_2['f1']:.3f}")
        print(f"  ROUGE-L F1: {rouge_l['f1']:.3f}")
        print(f"  TF-IDF Similarity: {semantic_tfidf:.3f}")
        print(f"  Jaccard Similarity: {semantic_jaccard:.3f}")
        print(f"  Sequence Similarity: {semantic_sequence:.3f}")
        
        # Verify all_metrics matches individual calculations
        assert abs(all_metrics['bleu_score'] - bleu) < 0.001, "BLEU score mismatch"
        assert abs(all_metrics['rouge_scores']['rouge-1']['f1'] - rouge_1['f1']) < 0.001, "ROUGE-1 F1 mismatch"
        assert abs(all_metrics['rouge_scores']['rouge-2']['f1'] - rouge_2['f1']) < 0.001, "ROUGE-2 F1 mismatch"
        assert abs(all_metrics['rouge_scores']['rouge-l']['f1'] - rouge_l['f1']) < 0.001, "ROUGE-L F1 mismatch"
        assert abs(all_metrics['semantic_similarity']['tfidf'] - semantic_tfidf) < 0.001, "TF-IDF similarity mismatch"
        assert abs(all_metrics['semantic_similarity']['jaccard'] - semantic_jaccard) < 0.001, "Jaccard similarity mismatch"
        assert abs(all_metrics['semantic_similarity']['sequence'] - semantic_sequence) < 0.001, "Sequence similarity mismatch"
        
        print("  ✅ All metrics calculated correctly")
    
    print("\n🎉 All tests passed! Advanced metrics are working correctly.")
    print("\n📊 Expected Results:")
    print("- Exact Match: Should have high scores across all metrics")
    print("- Similar Meaning: Should have moderate-high semantic similarity, lower BLEU/ROUGE")
    print("- Partial Match: Should have moderate scores across all metrics")
    print("- Different Content: Should have low scores across all metrics")

if __name__ == "__main__":
    try:
        test_advanced_metrics()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1) 