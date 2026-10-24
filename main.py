from fastapi import FastAPI
from router import NexusV10_EdgeRouter

app = FastAPI(
    title="NEXUS ENGINE V10",
    description="V10 PRO - Smart Edge Router | Owner: Abhishek Pal",
    version="10.0"
)

router = NexusV10_EdgeRouter()

@app.get("/")
def home():
    return {
        "project": "NEXUS ENGINE V10 - Smart Edge Router",
        "owner": "Abhishek Pal",
        "location": "Jamshedpur, India",
        "status": "PRO - Hysteresis + Cooldown Active",
        "current_target": router.current_target,
        "stats": router.stats,
        "live_url": "https://nexus-engine-v10.onrender.com"
    }

@app.get("/route")
def check_route():
    target = router.route_request()
    ram = router.get_real_ram()
    return {"ram_free_mb": round(ram, 2), "routed_to": target}
