# Chatbot Akademik Pemrograman Jaringan 🔌💻

Aplikasi Chatbot AI akademik berbasis Streamlit yang dirancang khusus untuk membahas mata kuliah **Pemrograman Jaringan (Network Programming)**. Proyek ini siap digunakan sebagai tugas besar / Ujian Akhir Semester (UAS) dengan kualitas production-ready, menggunakan clean architecture, modular, dan siap dideploy ke Streamlit Cloud.

---

## 📐 Arsitektur Sistem

Aplikasi ini dideploy pada **Streamlit Cloud** dan terhubung ke dua layanan eksternal:
1. **Neon PostgreSQL 17 (Cloud Database)**: Untuk menyimpan riwayat obrolan (session & message) dan logs request secara persisten meskipun komputer lokal Anda dimatikan.
2. **LM Studio + ngrok (Local LLM Server)**: LM Studio berjalan secara lokal untuk menjalankan model bahasa besar (LLM). Terowongan HTTPS aman dibuat menggunakan **ngrok** agar Streamlit Cloud dapat mengirim prompt ke LM Studio lokal Anda.

### Diagram Arsitektur Alur Request-Response

```mermaid
graph TD
    User([User Client / Browser]) <-->|HTTPS| Streamlit[Streamlit Cloud]
    
    subgraph Cloud Infrastructure
        Streamlit <-->|SSL JDBC/PG| Neon[(Neon PostgreSQL 17)]
    end
    
    subgraph Local Computer
        Ngrok[ngrok HTTPS Tunnel] <-->|Port 1234| LMStudio[LM Studio Server]
        LMStudio <--> LocalLLM[Local LLM]
    end
    
    Streamlit <-->|HTTPS API requests| Ngrok
```

> [!IMPORTANT]
> - **Neon PostgreSQL** berada di cloud, sehingga data dan log monitoring tetap tersimpan secara aman di cloud database.
> - **LM Studio dan ngrok** di komputer lokal Anda **harus tetap berjalan** agar chatbot dapat memproses pertanyaan dan menghasilkan jawaban.

---

## ✨ Fitur Utama

- ✔ **Desain Premium & Dark Mode Friendly**: Menggunakan tema gelap premium dengan gaya glassmorphism pada panel monitoring.
- ✔ **Dual Domain Validation**:
  - **Layer 1 (Keyword Validation)**: Memeriksa prompt secara lokal sebelum dikirim ke LLM. Jika tidak berkaitan dengan Pemrograman Jaringan, langsung menolak tanpa mengirim request API (menghemat token & latency).
  - **Layer 2 (System Instructions)**: Mengarahkan model agar tetap patuh hanya menjawab dalam domain Pemrograman Jaringan.
- ✔ **Session & Multi-User Management**: Setiap sesi chat memiliki Session UUID unik sehingga riwayat chat tidak tercampur antar pengguna.
- ✔ **Request-Response Logging**: Mencatat setiap aktivitas prompt, respon, status log, dan latency (ms) sebagai bukti implementasi protokol komunikasi.
- ✔ **Monitoring Dashboard**: Menampilkan statistik real-time: Uptime aplikasi, status koneksi database, status LM Studio, total session, request success/failed, dan average response time.
- ✔ **Suggested Questions**: Memberikan rekomendasi pertanyaan akademis yang dapat diklik langsung oleh pengguna.
- ✔ **AI Chat Experience**: Mendukung Markdown rendering, sintaks syntax highlighting untuk blok kode, streaming response, dan indikator penulisan (typing effect).

---

## 📂 Struktur Folder Proyek

```text
CHATBOT_PJAR/
├── .streamlit/
│   └── config.toml          # Konfigurasi Tema Streamlit (Dark Mode)
├── assets/
│   └── style.css            # Custom CSS untuk UI premium & Glassmorphic Dashboard
├── services/
│   ├── __init__.py
│   ├── chat_service.py      # Orkestrator alur chat, validasi, dan log
│   ├── history_service.py   # Pengelola database riwayat pesan & session
│   ├── llm_service.py       # Pengelola koneksi, status, & streaming LM Studio
│   ├── logging_service.py   # Pencatat request logs ke PostgreSQL
│   ├── prompts.py           # System prompts & daftar keyword Pemrograman Jaringan
│   └── validators.py        # Validator keyword lokal (Layer 1)
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Helper pencatat uptime & parser client header
├── app.py                   # Main Entrypoint UI Streamlit
├── config.py                # Driver Konfigurasi (Env Var & Streamlit Secrets)
├── database.py              # Koneksi Database & Connection Pool SQLAlchemy
├── models.py                # Definisi Model ORM (SQLAlchemy)
├── requirements.txt         # Daftar Dependencies python
├── .env.example             # Contoh template variabel lingkungan (.env)
├── .env                     # Variabel lingkungan lokal (diabaikan oleh git)
└── .gitignore               # Daftar file/folder yang diabaikan git
```

---

## 🛠️ Panduan Instalasi Lokal

### 1. Kloning Repositori & Persiapan
Buka terminal/command prompt pada komputer Anda dan masuk ke direktori proyek:
```bash
cd "PATH_TO_YOUR_PROJECT/CHATBOT_PJAR"
```

### 2. Membuat Virtual Environment (`chatbot_uas_pjar`)

Ikuti perintah sesuai sistem operasi yang Anda gunakan:

#### **Windows CMD**
```cmd
python -m venv chatbot_uas_pjar
chatbot_uas_pjar\Scripts\activate
```

#### **Windows PowerShell**
```powershell
python -m venv chatbot_uas_pjar
.\chatbot_uas_pjar\Scripts\Activate.ps1
```
*Catatan: Jika muncul error Permission Denied di PowerShell, jalankan `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` terlebih dahulu.*

#### **Linux**
```bash
python3 -m venv chatbot_uas_pjar
source chatbot_uas_pjar/bin/activate
```

#### **MacOS**
```bash
python3 -m venv chatbot_uas_pjar
source chatbot_uas_pjar/bin/activate
```

### 3. Menginstal Dependency
Setelah virtual environment aktif, jalankan perintah berikut:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🤖 Menjalankan LM Studio & ngrok

Chatbot menggunakan LM Studio sebagai backend model bahasa lokal dan ngrok sebagai terowongan HTTPS agar dapat diakses oleh server Streamlit Cloud.

### 1. Menjalankan LM Studio
1. Buka aplikasi **LM Studio**.
2. Unduh model pilihan Anda (misalnya `qwen2.5-coder-7b` atau `llama-3`).
3. Buka tab **Local Server** (ikon panah/developer di menu kiri).
4. Pilih model yang telah diunduh di dropdown bagian atas.
5. Klik tombol **Start Server**. Port default yang digunakan adalah `1234`.
6. Pastikan API OpenAI Compatible diaktifkan. LM Studio sekarang dapat diakses secara lokal di `http://localhost:1234`.

### 2. Menginstal dan Menjalankan ngrok
ngrok digunakan untuk mem-forward server lokal LM Studio ke internet melalui URL HTTPS publik.

1. **Instalasi ngrok**: Unduh ngrok dari [ngrok.com](https://ngrok.com/) atau gunakan package manager (seperti `brew install ngrok` di macOS atau `choco install ngrok` di Windows).
2. **Koneksi Akun**: Dapatkan authtoken dari dashboard ngrok Anda dan jalankan perintah otentikasi:
   ```bash
   ngrok config add-authtoken <TOKEN_ANDA>
   ```
3. **Membuka Tunnel**: Forward port lokal `1234` tempat LM Studio berjalan ke internet:
   ```bash
   ngrok http 1234
   ```
4. ngrok akan menampilkan informasi tunnel yang aktif. Salin alamat forwarding HTTPS yang berakhiran `.ngrok-free.app` (misalnya: `https://7fae-110-138-93-238.ngrok-free.app`).

### 3. Konfigurasi File `.env` lokal
Ganti nilai konfigurasi di file `.env` proyek Anda dengan URL ngrok tersebut. Pastikan Anda menambahkan `/v1` di akhir URL.
```env
DATABASE_URL=postgresql://neondb_owner:npg_CO0SejPiQ9Vt@ep-round-dust-ats816vb.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require
LLM_BASE_URL=https://7fae-110-138-93-238.ngrok-free.app/v1
MODEL_NAME=qwopus3.5-9b-coder
API_KEY=lm-studio
TEMPERATURE=0.3
MAX_TOKENS=4096
APP_TITLE=Chatbot Pemrograman Jaringan
LOG_LEVEL=INFO
DEBUG=False
```

---

## 🚀 Menjalankan Aplikasi di Lokal

Setelah semua konfigurasi selesai dan virtual environment aktif:
```bash
streamlit run app.py
```
Aplikasi akan terbuka otomatis di browser Anda pada alamat `http://localhost:8501`.

---

## ☁️ Mendeploy ke Streamlit Cloud

Aplikasi ini sepenuhnya siap dijalankan di Streamlit Cloud dengan langkah-langkah mudah berikut:

### 1. Push Code ke GitHub
1. Pastikan Anda tidak menyertakan file `.env` ke GitHub (pastikan file tersebut ada di daftar `.gitignore`).
2. Buat repositori baru di GitHub.
3. Commit dan push seluruh kode Anda ke repositori tersebut:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Network Programming Chatbot Production Ready"
   git branch -M main
   git remote add origin <URL_REPOS_GITHUB>
   git push -u origin main
   ```

### 2. Deploy di Streamlit Share
1. Masuk ke [share.streamlit.io](https://share.streamlit.io/) menggunakan akun GitHub Anda.
2. Klik tombol **New App**.
3. Pilih repositori, branch (`main`), dan main file path (`app.py`).
4. Klik pada bagian **Advanced Settings...**.
5. Di bagian **Secrets**, tempel isi file `.env` Anda dengan format TOML berikut:
   ```toml
   DATABASE_URL = "postgresql://neondb_owner:npg_CO0SejPiQ9Vt@ep-round-dust-ats816vb.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require"
   LLM_BASE_URL = "https://7fae-110-138-93-238.ngrok-free.app/v1"
   MODEL_NAME = "qwopus3.5-9b-coder"
   API_KEY = "lm-studio"
   TEMPERATURE = 0.3
   MAX_TOKENS = 4096
   APP_TITLE = "Chatbot Pemrograman Jaringan"
   LOG_LEVEL = "INFO"
   DEBUG = false
   ```
6. Klik **Save** kemudian klik **Deploy**. Aplikasi Anda akan berjalan langsung di cloud!

---

## 🛠️ Troubleshooting & FAQ

### ❓ Kenapa Chatbot Langsung Menolak Pertanyaan Saya?
* **Penyebab**: Pertanyaan Anda terdeteksi tidak relevan dengan Pemrograman Jaringan (gagal di validasi Layer 1: Keyword Validation).
* **Solusi**: Pastikan pertanyaan Anda mengandung kata kunci terkait jaringan seperti *TCP, UDP, Socket, IP Address, Port, Routing*, dll.

### ❓ Kenapa Muncul Status Disconnected pada LM Studio?
* **Penyebab**: Terowongan ngrok Anda telah mati, atau alamat forwarding ngrok berubah setelah Anda me-restart terminal ngrok.
* **Solusi**: Jalankan kembali `ngrok http 1234`, salin URL HTTPS baru dari ngrok, dan perbarui nilai `LLM_BASE_URL` di file `.env` lokal Anda atau di bagian Secrets Streamlit Cloud. Jangan lupa tambahkan `/v1` di akhir URL.

### ❓ Apakah Data Riwayat Percakapan Hilang Jika Komputer Dimatikan?
* **Penyebab**: Tidak. Database menggunakan **Neon PostgreSQL 17** yang berada di cloud. Data riwayat chat dan request logs tersimpan dengan aman di server cloud Neon dan tidak bergantung pada status komputer lokal Anda.

### ❓ Mengapa Respon AI Sangat Lambat atau Mengalami Connection Timeout?
* **Penyebab**: Jaringan internet lokal Anda atau bandwidth ngrok sedang mengalami throttling, atau spesifikasi komputer lokal Anda tidak kuat untuk mengoperasikan LLM di LM Studio secara real-time.
* **Solusi**: Gunakan model LLM lokal yang berukuran lebih kecil (misalnya model 1.5B atau 3B) di LM Studio untuk meningkatkan kecepatan pemrosesan respon.
