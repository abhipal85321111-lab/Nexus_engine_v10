import time
import psutil
from fastapi import FastAPI

class NexusV10_EdgeRouter:
    """V10 PRO - Smart Edge Router with Hysteresis + Cooldown"""

    def __init__(self):
        self.last_edge_switch = 0
        self.cooldown = 5  # 5 sec tak wapas local pe nahi ayega - flapping rokta hai
        self.low_threshold = 150  # MB
        self.high_threshold = 300  # MB - wapas aane ke liye
        self.current_target = "LOCAL_DEVICE"
        self.stats = {"local": 0, "edge": 0}

    def get_real_ram(self):
        """Real RAM check"""
        try:
            return psutil.virtual_memory().available / (1024 * 1024)
        except:
            return 9999

    def route_request(self, ram_free_mb=None):
        if ram_free_mb is None:
            ram_free_mb = self.get_real_ram()
        
        now = time.time()

        if ram_free_mb < self.low_threshold:
            if self.current_target != "EDGE_CLOUD":
                print(f"[v10] RAM {ram_free_mb:.0f}MB < {self.low_threshold}MB! -> EDGE_CLOUD")
                self.current_target = "EDGE_CLOUD"
                self.last_edge_switch = now
            else:
                print(f"[v10] RAM {ram_free_mb:.0f}MB - Still on EDGE")

        elif ram_free_mb > self.high_threshold:
            if now - self.last_edge_switch > self.cooldown:
                if self.current_target != "LOCAL_DEVICE":
                    print(f"[v10] RAM {ram_free_mb:.0f}MB > {self.high_threshold}MB, Cooldown done -> LOCAL_DEVICE")
                    self.current_target = "LOCAL_DEVICE"
            else:
                left = self.cooldown - (now - self.last_edge_switch)
                print(f"[v10] RAM recovered {ram_free_mb:.0f}MB but cooldown {left:.1f}s left -> Stay on EDGE")
        else:
            print(f"[v10] RAM {ram_free_mb:.0f}MB in buffer zone -> Stay on {self.current_target}")

        self.stats["local" if self.current_target == "LOCAL_DEVICE" else "edge"] += 1
        return self.current_target

# --- FastAPI Live Server ---
app = FastAPI(title="NEXUS ENGINE V10.1 PRO")
engine = NexusV10_EdgeRouter()

@app.get("/")
def home():
    return {
        "project": "NEXUS ENGINE V10.1 PRO",
        "owner": "Abhishek Pal",
        "status": "LIVE",
        "current_routing": engine.current_target,
        "live_ram_mb": round(engine.get_real_ram(), 2),
        "stats": engine.stats,
        "logic": "150MB Low / 300MB High + 5s Cooldown"
    }

@app.get("/route")
def get_route():
    target = engine.route_request()
    return {"ram_free_mb": round(engine.get_real_ram(), 2), "routed_to": target}
