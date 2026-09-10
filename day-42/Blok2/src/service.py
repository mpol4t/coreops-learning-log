from src.client import load_assets

def get_owner_summary(owner):
    assets = load_assets(owner)
    if not assets:
        return {
            "owner:": owner,
            "count:": len(assets),
            "status:": "empty",
        }
    
    return {
        "owner:": owner,
        "count:": len(assets),
        "status:": "ok",
    }