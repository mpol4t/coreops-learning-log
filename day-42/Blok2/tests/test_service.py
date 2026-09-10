import pytest
import src.service as service

def test_get_owner_summary_success(monkeypatch):
    def fake_load_assets(owner):
        return [
            {"hostname": "a.local"},
            {"hostname": "b.local"},
        ]
    
    monkeypatch.setattr(
        service,
        "load_assets",
        fake_load_assets
    )
    
    result = service.get_owner_summary("blue-team")
    
    assert result == {
        "owner:": "blue-team",
        "count:": 2,
        "status:": "ok",
    }
    

def test_get_owner_summary_empty(monkeypatch):
    def fake_load_assets(owner):
        return []
    
    monkeypatch.setattr(
        service,
        "load_assets",
        fake_load_assets
    )
    
    result = service.get_owner_summary("blue-team")
    
    assert result == {
        "owner:": "blue-team",
        "count:": 0,
        "status:": "empty",
    }
    
def test_get_owner_summary_error(monkeypatch):
    def fake_load_assets(owner):
        raise ConnectionError
    
    monkeypatch.setattr(
        service,
        "load_assets",
        fake_load_assets
    )
    
    with pytest.raises(ConnectionError):
        service.get_owner_summary("blue-team")
        
