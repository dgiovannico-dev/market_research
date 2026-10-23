from app.llm.gold_eval import evaluate_gold_labels


def test_gold_labels_score_rules_classifier():
    result = evaluate_gold_labels()
    assert result["method"] == "gold_labels_rules"
    assert result["items_evaluated"] >= 5
    assert result["overall_accuracy"] is not None
    assert result["overall_accuracy"] >= 0.8
    assert result["field_accuracy"]["contract_type"] is not None
    assert result["field_accuracy"]["remote_type"] is not None
