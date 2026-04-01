# TikTok Emulator Setup — 6-Layer Bypass Guide

ตั้งค่า Android emulator ให้รัน TikTok ได้โดยไม่โดน Gorgon detection

## Prerequisites

- Android Studio (with AVD Manager)
- ADB in PATH
- Python 3.10+
- Git

## Layer 1: Create AVD + Root with Magisk

### สร้าง AVD

```bash
# Android Studio → Device Manager → Create Device
# Device: Pixel 8
# System Image: API 34 (Android 14), x86_64
# Boot option: Cold boot (สำคัญ!)
```

### Root ด้วย rootAVD

```bash
git clone https://github.com/newbit1/rootAVD.git
cd rootAVD

# List AVDs
./rootAVD.sh ListAllAVDs

# Root (ใช้ FAKEBOOTIMG สำหรับ Magisk 26+)
./rootAVD.sh system-images/android-34/google_apis/x86_64/ramdisk.img FAKEBOOTIMG
```

### ติดตั้ง Shamiko

1. เปิด Magisk app → Settings → เปิด Zygisk
2. **ปิด** Enforce DenyList
3. DenyList → เพิ่ม `com.zhiliaoapp.musically` (TikTok)
4. ดาวน์โหลด [Shamiko](https://github.com/LSPosed/LSPosed.github.io/releases) → Install from storage
5. Reboot (cold boot)

## Layer 2: Spoof Device Identity

### ติดตั้ง Komodo Build Prop module

```bash
# ดาวน์โหลดจาก https://github.com/Elcapitanoe/Komodo-Build-Prop
# Magisk → Modules → Install from storage → เลือก zip
# Reboot
```

Module จะ spoof props เป็น Pixel 9 Pro XL:
- `ro.product.model`, `ro.product.brand`, `ro.product.device`
- `ro.hardware` (ลบ goldfish/ranchu)
- `ro.build.fingerprint` (จาก firmware จริง)

### ตรวจสอบ

```bash
adb shell getprop ro.product.model    # ต้องเห็น Pixel 9 Pro XL
adb shell getprop ro.hardware         # ต้องไม่เป็น goldfish
```

## Layer 3: Play Integrity

### ติดตั้ง PlayIntegrityFork

```bash
# ดาวน์โหลดจาก https://github.com/osm0sis/PlayIntegrityFork
# Magisk → Modules → Install from storage
# Reboot
```

หมายเหตุ: Emulator จะได้แค่ `MEETS_BASIC_INTEGRITY` — ไม่ได้ DEVICE level เต็ม

## Layer 4: Sensor Spoofing

### วิธีที่ 1: Android Studio Extended Controls

```
Emulator → ... (More) → Virtual Sensors
→ ปรับ Accelerometer, Gyroscope, Magnetometer
→ เปิด "Play recorded motion" ถ้ามี
```

### วิธีที่ 2: PriviSense (Frida-based, ขั้นสูง)

```bash
# ต้อง root + frida-server
pip install frida-tools
adb push frida-server /data/local/tmp/
adb shell chmod 755 /data/local/tmp/frida-server
adb shell /data/local/tmp/frida-server &

# Inject sensor data
frida -U -f com.zhiliaoapp.musically -l sensor_spoof.js
```

สำคัญ: ต้องเพิ่ม random noise ให้ sensor data ไม่คงที่

## Layer 5: Network

### ใช้ Residential Proxy

```bash
# ตั้ง proxy บน emulator
adb shell settings put global http_proxy <proxy_ip>:<port>

# หรือใช้ VPN app บน emulator
# แนะนำ: Residential proxy (ไม่ใช่ datacenter)
```

## Layer 6: uiautomator2 Setup

```bash
pip install uiautomator2
python -m uiautomator2 init    # Install ATX agent on device

# ทดสอบเชื่อมต่อ
python -c "import uiautomator2 as u2; d = u2.connect(); print(d.info)"
```

Shamiko จะซ่อน `com.github.uiautomator` จาก TikTok (ถ้าเพิ่มใน DenyList)

## ทดสอบ

```bash
# 1. เปิด TikTok ดูว่ารันได้ไหม
adb shell am start -n com.zhiliaoapp.musically/.MainTabActivity

# 2. Login ด้วยมือก่อน ดูว่าไม่โดน ban

# 3. ทดสอบ bot
python run.py --once
```

## ข้อควรระวัง

- **Cold boot เสมอ** — Quick boot อาจทำให้ Magisk พัง
- **บัญชีใหม่เสี่ยงกว่าบัญชีเก่า** — ใช้บัญชีที่มีอยู่แล้วดีกว่า
- **TikTok ปรับ detection ตลอด** — bypass อาจหมดอายุใน 2-4 สัปดาห์
- **เริ่มช้า** — ไม่ like/comment เยอะตั้งแต่แรก ค่อยๆ เพิ่ม
- **Residential proxy สำคัญ** — datacenter IP โดน flag ทันที
