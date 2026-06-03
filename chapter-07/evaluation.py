# evaluation.py
"""RAG system evaluation pipeline."""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class EvalResult:
    question: str
    expected_answer: str
    actual_answer: str
    documents_retrieved: List[str]
    correct_document_retrieved: bool
    rank_of_correct: int
    answer_correct: bool


class RAGEvaluator:
    """Evaluate RAG system performance."""

    def __init__(self, query_engine) -> None:
        self.query_engine = query_engine

    def evaluate(self, test_cases: List[Dict]) -> List[EvalResult]:
        """Run evaluation on test cases."""
        results = []
        for case in test_cases:
            # Query the system
            response = self.query_engine.query(case["question"])

            # Check if correct document was retrieved
            retrieved_docs = [
                n.metadata.get("source", "") for n in response.source_nodes
            ]

            correct_retrieved = case["expected_source"] in retrieved_docs
            rank = (
                retrieved_docs.index(case["expected_source"]) + 1
                if correct_retrieved
                else -1
            )

            # Check answer accuracy (simplified)
            answer_correct = case["expected_answer"].lower() in str(response).lower()

            results.append(
                EvalResult(
                    question=case["question"],
                    expected_answer=case["expected_answer"],
                    actual_answer=str(response),
                    documents_retrieved=retrieved_docs,
                    correct_document_retrieved=correct_retrieved,
                    rank_of_correct=rank,
                    answer_correct=answer_correct,
                )
            )

        return results

    def summary(self, results: List[EvalResult]) -> Dict:
        """Generate evaluation summary."""
        total = len(results)
        hit_rate = sum(1 for r in results if r.correct_document_retrieved) / total
        answer_accuracy = sum(1 for r in results if r.answer_correct) / total

        # MRR
        reciprocal_ranks = [
            1 / r.rank_of_correct if r.rank_of_correct > 0 else 0 for r in results
        ]
        mrr = sum(reciprocal_ranks) / total

        return {
            "total_cases": total,
            "hit_rate": hit_rate,
            "answer_accuracy": answer_accuracy,
            "mrr": mrr,
        }
