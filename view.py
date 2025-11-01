import random, requests, re, threading, time, secrets, os
from hashlib import md5
from time import time as T

# --------------------- GIAO DIỆN ---------------------
os.system("cls" if os.name == "nt" else "clear")
print("╔══════════════════════════════════════════╗")
print("║        🌟 TIKTOK VIEW BOT v2.0 🌟        ║")
print("║                                                                 ")
print("╚══════════════════════════════════════════╝\n")

# --------------------- RANDOM DEVICE ---------------------
def random_device():
    devices = ["Pixel 6", "Pixel 5", "Galaxy S21", "Oppo Reno 8", "Xiaomi Mi 11"]
    os_versions = ["12", "13", "14"]
    return random.choice(devices), random.choice(os_versions), random.randint(26, 34)

# --------------------- SIGNATURE CLASS ---------------------
class Signature:
    def __init__(self, params, data, cookies):
        self.params, self.data, self.cookies = params, data, cookies

    def hash(self, data): 
        return md5(data.encode()).hexdigest()

    def calc_gorgon(self):
        g = self.hash(self.params)
        g += self.hash(self.data) if self.data else "0" * 32
        g += self.hash(self.cookies) if self.cookies else "0" * 32
        return g + "0" * 32

    def get_value(self):
        return self.encrypt(self.calc_gorgon())

    def encrypt(self, data):
        unix, length = int(T()), 0x14
        key = [0xDF,0x77,0xB9,0x40,0xB9,0x9B,0x84,0x83,0xD1,0xB9,0xCB,0xD1,0xF7,0xC2,0xB9,0x85,0xC3,0xD0,0xFB,0xC3]
        pl = []
        for i in range(0, 12, 4):
            t = data[8 * i:8 * (i + 1)]
            for j in range(4):
                pl.append(int(t[j * 2:(j + 1) * 2], 16))
        pl.extend([0x0, 0x6, 0xB, 0x1C])
        H = unix
        pl += [(H >> 24) & 255, (H >> 16) & 255, (H >> 8) & 255, H & 255]
        e = [a ^ b for a, b in zip(pl, key)]
        for i in range(length):
            C = int(bin(e[i])[2:].zfill(8)[::-1], 2)
            D = e[(i + 1) % length]
            F = int(bin(C ^ D)[2:].zfill(8)[::-1], 2)
            e[i] = ((F ^ 0xFFFFFFFF) ^ length) & 0xFF
        r = "".join(hex(x)[2:].zfill(2) for x in e)
        return {"X-Gorgon": "840280416000" + r, "X-Khronos": str(unix)}

# --------------------- LẤY ID VIDEO ---------------------
link = input("🔗 Nhập link video TikTok: ").strip()
headers_id = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/127.0.0.0 Safari/537.36'}

try:
    page = requests.get(link, headers=headers_id, timeout=10).text
    video_id = re.search(r'"video":\{"id":"(\d+)"', page).group(1)
    print(f"✅ Đã tìm thấy ID Video: {video_id}\n")
except Exception:
    print("❌ Không thể lấy ID Video. Kiểm tra lại link!")
    exit()

# --------------------- USER-AGENT DANH SÁCH ---------------------
ua_list = [
    "com.ss.android.ugc.trill/400304 (Linux; Android 13; vi_VN; Pixel 6)",
    "com.ss.android.ugc.trill/400304 (Linux; Android 12; vi_VN; Galaxy S21)",
    "com.ss.android.ugc.trill/400304 (Linux; Android 14; vi_VN; Mi 11)"
]

# --------------------- HÀM GỬI VIEW ---------------------
def send_view():
    device_type, os_version, os_api = random_device()
    params = (
        f"channel=googleplay&aid=1233&app_name=musical_ly&version_code=400304"
        f"&device_platform=android&device_type={device_type.replace(' ', '+')}"
        f"&os_version={os_version}&device_id={random.randint(int(6e14), int(7e14))}"
        f"&os_api={os_api}&app_language=vi&tz_name=Asia%2FHo_Chi_Minh"
    )
    url = f"https://api16-core-c-alisg.tiktokv.com/aweme/v1/aweme/stats/?{params}"
    cookies = {"sessionid": secrets.token_hex(8)}

    while True:
        data = {"item_id": video_id, "play_delta": 1, "action_time": int(time.time())}
        sig = Signature(params, str(data), str(cookies)).get_value()
        headers = {
            "User-Agent": random.choice(ua_list),
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Gorgon": sig["X-Gorgon"],
            "X-Khronos": sig["X-Khronos"]
        }
        try:
            r = requests.post(url, data=data, headers=headers, cookies=cookies, timeout=10)
            if r.ok:
                print(f"\033[92m[+] View thành công!\033[0m")
        except:
            pass
        time.sleep(random.uniform(0.3, 1.2))

# --------------------- CHẠY NHIỀU LUỒNG ---------------------
threads = []
for i in range(300):  # Giảm còn 300 luồng để đỡ lag
    t = threading.Thread(target=send_view, daemon=True)
    t.start()
    threads.append(t)

for t in threads:
    t.join()