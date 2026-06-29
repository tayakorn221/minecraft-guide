# 📁 Minecraft — รวมไฟล์/เอกสาร

จัดระเบียบเมื่อ 2026-06-29 รวมไฟล์ที่เคยกระจายอยู่ (Downloads + temp) มาไว้ที่เดียว

> 🌐 **เว็บคู่มือ (live):** https://tayakorn221.github.io/minecraft-guide/ — ธีมตำราเวท เปิดอ่านในเบราว์เซอร์/มือถือได้เลย

## โครงสร้างโฟลเดอร์
```
Documents\Minecraft\
├── docs\        คู่มือ/เอกสาร
├── modpacks\    ไฟล์ .mrpack สำรอง
└── backups\     สำรอง mods (กันพัง ย้อนกลับได้)
```

## 📦 สอง setup ที่เล่นอยู่

### 1. MC 26.1.2 (หลัก — เล่นกับเพื่อน)
- **Game:** `C:\Users\User\AppData\Roaming\.minecraft\` (profile `fabric-loader-26.1.2`)
- **Server:** `C:\Users\User\MinecraftServer\` (start.bat)
- **บันทึกการตั้งค่า/มอด:** `.minecraft\CLAUDE.md`
- **Backup mods:** `backups\client-mods-26.1.2-backup-2026-06-28.zip` + `server-...zip`
  - ถ้ามอดพัง → แตก zip ทับโฟลเดอร์ `mods\` กลับได้

### 2. MC 1.21.1 — RPG Origins (แยก, มอด overhaul)
- **Launcher:** Prism Launcher 11.0.2
- **Instance:** `C:\Users\User\AppData\Roaming\PrismLauncher\instances\RPG Origins 13.7.0\`
- **Modpack:** RPG Origins - Rise of Power v13.7.0 (สำรองที่ `modpacks\`)
- **RAM:** 6144 MB (6GB)
- **คู่มือเผ่า 27 เผ่า:** `docs\RPG-Origins-คู่มือเผ่า.md`

## ไฟล์ในนี้
| ไฟล์ | คือ |
|---|---|
| **`docs\INDEX.md`** | 📚 **สารบัญคู่มือทั้งหมด — เริ่มที่นี่** (ลิงก์ 6 ไฟล์ จัดกลุ่มตาม 2 setup) |
| `docs\` (6 ไฟล์ .md + 1 .html) | คู่มือเผ่า, เลือกเผ่า, เริ่มเล่น, ปุ่มพลัง, เข้าเซิร์ฟเพื่อน, มอดใหม่ 26.1.2 + origin-selector.html |
| `modpacks\RPG Origins 13.7.0.mrpack` | ไฟล์ modpack สำรอง (เผื่อ import ใหม่) |
| `backups\*.zip` | สำรอง mods 26.1.2 ก่อนเพิ่มชุดบอส/QoL |

## ✅ สถานะงาน
**เสร็จแล้ว (2026-06-29):** ชุดคู่มือครบ 6 ไฟล์ใน `docs\` — เนื้อหาทุกตัวเลข/สูตร/ปุ่ม ตรวจสอบกับไฟล์มอดจริง (jar) แล้ว ดูสารบัญที่ [`docs\INDEX.md`](docs/INDEX.md)
- คู่มือเผ่า 27 ตัว · เลือกเผ่า (decision) · เริ่มเล่น (getting started) · ปุ่มพลัง active · เข้าเซิร์ฟเพื่อน 26.1.2 · มอดใหม่ 26.1.2
- หน้าเว็บ `origin-selector.html` (interactive) — สร้างแล้ว

**เฟส HTML (เสร็จแล้ว):** แปลงคู่มือ `.md` → เว็บ HTML ธีม "ตำราเวท" (เข้าชุด `origin-selector.html`) + GitHub Pages
- 🌐 live: https://tayakorn221.github.io/minecraft-guide/
- รีบิลด์ได้: แก้ `.md` แล้วรัน `python build_site.py` (ใช้ Python + `markdown`)
