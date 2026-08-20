from asset_model.models import Asset

asset = Asset(
    asset_id="server01", hostname="web01", port=443, active=True, tags=["web"]
)

print(asset)
