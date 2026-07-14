import os
from datetime import datetime
from db_manager import DEFAULT_STATE

def test_get_state_returns_default(db_mgr):
    """Test that get_state returns a copy of the default state if no file exists."""
    state = db_mgr.get_state()
    assert state["user_id"] == "default_student"
    assert state["overall_progress_percent"] == 0.0
    assert len(state["active_struggles"]) == 0
    assert len(state["quiz_history"]) == 0

def test_save_and_recalculate_progress(db_mgr):
    """Test saving state and that progress is recalculated dynamically."""
    state = db_mgr.get_state()
    # Manually complete a module in the state object
    state["modules"]["s1_m1"]["completed"] = True
    state["modules"]["s1_m1"]["hours_completed"] = 8.5
    
    db_mgr.save_state(state)
    
    saved_state = db_mgr.get_state()
    assert saved_state["modules"]["s1_m1"]["completed"] is True
    # Overall total is 69.25, s1_m1 is 8.5 hours. 8.5 / 69.25 * 100 = 12.27% -> 12.3%
    assert saved_state["overall_progress_percent"] == 12.3
    assert saved_state["hours_completed"] == 8.5

def test_log_struggle(db_mgr):
    """Test logging a learning struggle and avoiding duplicates."""
    db_mgr.log_struggle("Model Armor", "high")
    
    state = db_mgr.get_state()
    assert len(state["active_struggles"]) == 1
    assert state["active_struggles"][0]["topic"] == "Model Armor"
    assert state["active_struggles"][0]["severity"] == "high"
    assert state["active_struggles"][0]["status"] == "active"
    
    # Try logging duplicate active struggle
    db_mgr.log_struggle("Model Armor", "high")
    state = db_mgr.get_state()
    assert len(state["active_struggles"]) == 1

def test_resolve_struggle(db_mgr):
    """Test resolving an active struggle."""
    db_mgr.log_struggle("Antigravity CLI (agy)", "medium")
    db_mgr.resolve_struggle("Antigravity CLI (agy)")
    
    state = db_mgr.get_state()
    assert len(state["active_struggles"]) == 1
    assert state["active_struggles"][0]["status"] == "resolved"
    assert "resolved_at" in state["active_struggles"][0]

def test_add_quiz_result_fail(db_mgr):
    """Test adding a failing quiz result (< 80%) does not auto-complete module."""
    db_mgr.log_struggle("antigravity", "medium")
    db_mgr.add_quiz_result("s1_m1", 50.0)
    
    state = db_mgr.get_state()
    assert len(state["quiz_history"]) == 1
    assert state["quiz_history"][0]["score_percent"] == 50.0
    assert state["modules"]["s1_m1"]["completed"] is False
    assert state["active_struggles"][0]["status"] == "active"

def test_add_quiz_result_pass_resolves_struggles(db_mgr):
    """Test that a passing quiz score auto-completes module and resolves related struggles."""
    db_mgr.log_struggle("antigravity", "medium")
    db_mgr.add_quiz_result("s1_m1", 90.0)
    
    state = db_mgr.get_state()
    assert len(state["quiz_history"]) == 1
    assert state["modules"]["s1_m1"]["completed"] is True
    assert state["active_struggles"][0]["status"] == "resolved"
    assert state["overall_progress_percent"] == 12.3

def test_update_module_status(db_mgr):
    """Test manual module completion update."""
    db_mgr.update_module_status("s1_m2", True)
    
    state = db_mgr.get_state()
    assert state["modules"]["s1_m2"]["completed"] is True
    assert state["modules"]["s1_m2"]["hours_completed"] == 12.25
    # 12.25 / 69.25 * 100 = 17.689% -> 17.7%
    assert state["overall_progress_percent"] == 17.7
    
    db_mgr.update_module_status("s1_m2", False)
    state = db_mgr.get_state()
    assert state["modules"]["s1_m2"]["completed"] is False
    assert state["modules"]["s1_m2"]["hours_completed"] == 0.0
    assert state["overall_progress_percent"] == 0.0
