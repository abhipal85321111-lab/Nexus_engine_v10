import time
import psutil  # pip install psutil

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
            return 9999  # psutil nahi hai to local pe hi rakho

    def route_request(self, ram_free_mb=None):
        if ram_free_mb is None:
            ram_free_mb = self.get_real_ram()
        
        now = time.time()

        # HYSTERESIS LOGIC - Real ka magic yahi hai
        if ram_free_mb < self.low_threshold:
            # Low RAM - Edge pe bhejo
            if self.current_target != "EDGE_CLOUD":
                print(f"[v10] RAM {ram_free_mb:.0f}MB < {self.low_threshold}MB! -> EDGE_CLOUD")
                self.current_target = "EDGE_CLOUD"
                self.last_edge_switch = now
            else:
                print(f"[v10] RAM {ram_free_mb:.0f}MB - Still on EDGE")

        elif ram_free_mb > self.high_threshold:
            # RAM theek hua - Cooldown check
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

# ========== TERA TEST vs PRO TEST ==========
print("--- TERA V10 (Flapping Problem) ---")
v10_simple = NexusV10_EdgeRouter.__new__(NexusV10_EdgeRouter)
v10_simple.route_request = lambda ram: print(f"RAM {ram}MB -> {'EDGE' if ram < 150 else 'LOCAL'}") or ("EDGE_CLOUD" if ram < 150 else "LOCAL_DEVICE")
v10_simple.route_request(80)
v10_simple.route_request(160)  # turant wapas - flapping!
v10_simple.route_request(80)  # turant edge - bill double!

print("\n--- MERA V10.1 PRO (Real World) ---")
v10 = NexusV10_EdgeRouter()
v10.route_request(80)  # Edge pe gaya
v10.route_request(160)  # Buffer zone - Edge pe hi rahega
v10.route_request(320)  # High hua par cooldown me hai - Edge pe hi
time.sleep(5)
v10.route_request(320)  # Ab cooldown khatam - Wapas Local
print(f"\nStats: {v10.stats}")
