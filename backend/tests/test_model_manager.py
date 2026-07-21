from app.services.model_manager import model_manager

def test_model_manager_prediction():
    res = model_manager.predict("User login failed with HTTP 500 in OAuth authentication service", n_iter=10)
    assert "predicted_team" in res
    assert res["predicted_team"] in model_manager.label_to_id.values()
    assert res["confidence_score"] > 0.0
    assert "uncertainty_score" in res
    assert res["confidence_level"] in ["HIGH", "MEDIUM", "LOW"]
    assert len(res["top_alternatives"]) == 3
