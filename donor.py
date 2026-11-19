# ============================================================================
# PROGRAM SKRINING CALON PENDONOR DARAH - UTD PMI KOTA PONTIANAK
# ----------------------------------------------------------------------------
# Alur program:
#   1. Siapkan database lokal (SQLite) & sinkronkan file teks (.txt)
#   2. Tampilkan header + rekap total data terakhir dari database
#   3. Pilih menu: input skrining baru, lihat riwayat, atau lihat semua data (.txt)
#   4. Cek kriteria kelayakan & deteksi kondisi spesifik tubuh
#   5. Simpan data ke lokal, perbarui file .txt, dan cetak struk berwarna
# ============================================================================

from datetime import datetime
import sqlite3

# ----------------------------------------------------------------------------
# KODE WARNA ANSI
# Kode "\033[...m" dikenali terminal sebagai perintah untuk mengubah gaya teks.
# Teks yang dicetak setelah kode ini akan berwarna sampai bertemu RESET.
# ----------------------------------------------------------------------------
HIJAU = "\033[92m"   # hijau terang -> dipakai untuk status LOLOS
MERAH = "\033[91m"   # merah terang -> dipakai untuk status TIDAK LOLOS
KUNING = "\033[93m"  # kuning terang -> dipakai untuk pesan informasi
BIRU = "\033[94m"    # biru terang -> dipakai untuk garis dan judul
RESET = "\033[0m"    # mengembalikan teks ke warna/gaya normal
BOLD = "\033[1m"      # membuat teks menjadi tebal
HITAM = "\033[30m"    # sedangkan warna lain hanya untuk menghias saja
OREN = "\033[33m"
ABU = "\033[37m"
UNGU = "\033[35m"
PINK = "\033[95m"
CYAN = "\033[96m"
PUTIH = "\033[97m"   # putih terang

# Nama file penyimpanan lokal di folder yang sama dengan program
DB_FILE = "donor_pmi.db"
TXT_FILE = "rekap_pendonor.txt"


# ----------------------------------------------------------------------------
# FUNGSI DATABASE LOKAL (SQLITE) & EKSPOR TEKS (.TXT)
# Data disimpan ke SQLite agar total pendonor & riwayat tidak hilang saat
# program ditutup, sekaligus ditulis ke file teks agar mudah dibaca semua.
# ----------------------------------------------------------------------------
def init_db():
  """Membuat tabel pendonor di database lokal SQLite jika belum ada."""
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS pendonor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waktu_input TEXT,
            nama TEXT,
            usia INTEGER,
            berat_badan REAL,
            hb REAL,
            sistol INTEGER,
            diastol INTEGER,
            suhu REAL,
            jarak_donor INTEGER,
            status TEXT,
            catatan TEXT
        )
    """)
  conn.commit()
  conn.close()


def ambil_total_pendonor():
  """Mengambil jumlah total pendonor yang tersimpan di database lokal."""
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("SELECT COUNT(*) FROM pendonor")
  total = cursor.fetchone()[0]
  conn.close()
  return total


def ambil_ringkasan_status():
  """Mengambil jumlah pendonor LOLOS dan TIDAK LOLOS dari database."""
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("SELECT status, COUNT(*) FROM pendonor GROUP BY status")
  hasil = dict(cursor.fetchall())
  conn.close()
  return hasil.get("LOLOS", 0), hasil.get("TIDAK LOLOS", 0)


def ambil_riwayat_terakhir(limit=10):
  """Mengambil beberapa data pendonor terakhir untuk ditampilkan di menu."""
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      """
        SELECT id, waktu_input, nama, status, catatan
        FROM pendonor
        ORDER BY id DESC
        LIMIT ?
    """,
      (limit,),
  )
  rows = cursor.fetchall()
  conn.close()
  return rows


def export_semua_ke_txt():
  """Menulis seluruh data pendonor dari SQLite ke file teks (.txt)."""
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        SELECT id, waktu_input, nama, usia, berat_badan, hb,
               sistol, diastol, suhu, jarak_donor, status, catatan
        FROM pendonor
        ORDER BY id ASC
    """)
  rows = cursor.fetchall()
  conn.close()

  with open(TXT_FILE, "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("REKAP DATA SKRINING CALON PENDONOR - UTD PMI KOTA PONTIANAK\n")
    f.write(
        f"Diperbarui pada : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    f.write(f"Total Pendonor  : {len(rows)} orang\n")
    f.write("=" * 80 + "\n\n")

    if not rows:
      f.write("Belum ada data pendonor yang tersimpan.\n")
    else:
      for row in rows:
        (
            no_id,
            waktu,
            nama,
            usia,
            bb,
            hb,
            sistol,
            diastol,
            suhu,
            jarak,
            status,
            catatan,
        ) = row
        f.write(f"No. Urut      : #{no_id}\n")
        f.write(f"Waktu Input   : {waktu}\n")
        f.write(f"Nama Lengkap  : {nama}\n")
        f.write(f"Usia          : {usia} tahun\n")
        f.write(f"Berat Badan   : {bb} kg\n")
        f.write(f"Kadar Hb      : {hb} gr%\n")
        f.write(f"Tekanan Darah : {sistol}/{diastol} mmHg\n")
        f.write(f"Suhu Tubuh    : {suhu} °C\n")
        f.write(f"Jarak Donor   : {jarak} bulan\n")
        f.write(f"Status        : {status}\n")
        f.write(f"Catatan       : {catatan}\n")
        f.write("-" * 80 + "\n")


def simpan_pendonor(data):
  """Menyimpan satu data hasil skrining ke SQLite lalu memperbarui file .txt."""
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO pendonor (
            waktu_input, nama, usia, berat_badan, hb,
            sistol, diastol, suhu, jarak_donor, status, catatan
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          data["nama"].upper(),
          data["usia"],
          data["berat_badan"],
          data["hb"],
          data["sistol"],
          data["diastol"],
          data["suhu"],
          data["jarak_donor"],
          data["status"],
          data["catatan"],
      ),
  )
  conn.commit()
  conn.close()
  export_semua_ke_txt()


# ----------------------------------------------------------------------------
# FUNGSI BANTUAN INPUT AMAN
# Mencegah program error/crash jika petugas awam salah mengetik huruf
# pada kolom angka (atau memakai koma ',' untuk angka desimal).
# ----------------------------------------------------------------------------
def input_int(pesan):
  """Memastikan input berupa bilangan bulat valid."""
  while True:
    try:
      return int(input(pesan).strip())
    except ValueError:
      print(f"{MERAH}  [!] Input harus berupa angka bulat. Coba lagi.{RESET}")


def input_float(pesan):
  """Memastikan input berupa angka desimal/bulat valid."""
  while True:
    try:
      nilai = input(pesan).strip().replace(",", ".")
      return float(nilai)
    except ValueError:
      print(f"{MERAH}  [!] Input harus berupa angka. Coba lagi.{RESET}")


# ----------------------------------------------------------------------------
# FUNGSI ANALISIS KELAYAKAN & KONDISI SPESIFIK TUBUH
# Mengecek faktor fatal dan mengidentifikasi kondisi spesifik calon pendonor
# (seperti tekanan darah rendah/tinggi, kadar Hb rendah/tinggi, dll.).
# ----------------------------------------------------------------------------
def analisis_kelayakan(
    usia, berat_badan, hb, sistol, diastol, suhu, waktu_donor_terakhir
):
  """Mengembalikan list alasan gagal/kondisi spesifik jika ada yang melanggar."""
  alasan_gagal = []

  # --- Kriteria 1: Batas usia (17 - 65 tahun) ---
  if usia < 17 or usia > 65:
    alasan_gagal.append(
        f"Usia tidak memenuhi syarat (17-65 thn). Saat ini: {usia} tahun."
    )

  # --- Kriteria 2: Berat badan (minimal 45 kg) ---
  if berat_badan < 45:
    alasan_gagal.append(
        f"Berat badan kurang dari min. 45 kg. Saat ini: {berat_badan} kg."
    )

  # --- Kriteria 3: Kadar hemoglobin (12.5 - 17.0 gr%) ---
  if hb < 12.5:
    alasan_gagal.append(
        f"Kadar Hb terlalu rendah / indikasi kurang darah (< 12.5 gr%). Saat"
        f" ini: {hb} gr%."
    )
  elif hb > 17.0:
    alasan_gagal.append(
        f"Kadar Hb terlalu tinggi (> 17.0 gr%). Saat ini: {hb} gr%."
    )

  # --- Kriteria 4: Tekanan darah (sistol 90-120, diastol 70-100) ---
  # Diidentifikasi spesifik apakah mengarah ke darah rendah atau darah tinggi
  if sistol < 90 or diastol < 70:
    alasan_gagal.append(
        f"Tekanan darah rendah / hipotensi ({sistol}/{diastol} mmHg). Syarat"
        " sistol 90-120, diastol 70-100."
    )
  if sistol > 120 or diastol > 100:
    alasan_gagal.append(
        f"Tekanan darah tinggi / hipertensi ({sistol}/{diastol} mmHg). Syarat"
        " sistol 90-120, diastol 70-100."
    )

  # --- Kriteria 5: Suhu tubuh (35.0 - 38.0 °C) ---
  if suhu < 35.0:
    alasan_gagal.append(f"Suhu tubuh di bawah normal ({suhu} °C).")
  elif suhu > 38.0:
    alasan_gagal.append(f"Suhu tubuh demam / tinggi ({suhu} °C).")

  # --- Kriteria 6: Jarak dari donor terakhir (minimal 2 bulan) ---
  if waktu_donor_terakhir < 2:
    alasan_gagal.append(
        "Jarak waktu dari donor darah terakhir kurang dari 2 bulan"
        f" ({waktu_donor_terakhir} bln)."
    )

  return alasan_gagal


# ----------------------------------------------------------------------------
# FUNGSI cetak_header()
# Menampilkan judul instansi serta ringkasan jumlah pendonor terakhir dari
# database lokal SQLite.
# ----------------------------------------------------------------------------
def cetak_header():
  total = ambil_total_pendonor()
  lolos, tidak_lolos = ambil_ringkasan_status()

  print(f"{BIRU}{'='*80}{RESET}")
  print(
      f"{BOLD}{BIRU}                UNIT TRANSFUSI DARAH (UTD) PMI KOTA"
      f" PONTIANAK{RESET}"
  )
  print(f"{BIRU}{'='*80}{RESET}")
  print(
      "             Sistem Skrining & Identifikasi Otomatis Formulir Donor"
  )
  print(f"  Penyimpanan Lokal : {DB_FILE}  |  File Teks : {TXT_FILE}")
  print(
      f"  Total Terdata     : {KUNING}{total} orang{RESET}  |  "
      f"Lolos: {HIJAU}{lolos}{RESET}  |  "
      f"Tidak Lolos: {MERAH}{tidak_lolos}{RESET}"
  )
  print(f"{BIRU}{'-'*80}{RESET}\n")


# ----------------------------------------------------------------------------
# FUNGSI proses_skrining_baru()
# Mengambil input calon pendonor, menganalisis kelayakan, menyimpan ke lokal,
# dan mencetak struk hasil skrining berwarna.
# ----------------------------------------------------------------------------
def proses_skrining_baru():
  print(f"{BOLD}[+] MASUKKAN DATA CALON PENDONOR{RESET}")

  while True:
    nama = input("  - Nama Lengkap                 : ").strip()
    if nama:
      break
    print(f"{MERAH}  [!] Nama tidak boleh kosong.{RESET}")

  usia = input_int("  - Usia (tahun)                 : ")
  berat_badan = input_float("  - Berat Badan (kg)             : ")
  hb = input_float("  - Kadar Hemoglobin / Hb (gr%)  : ")
  sistol = input_int("  - Tekanan Darah Sistol (mmHg)  : ")
  diastol = input_int("  - Tekanan Darah Diastol (mmHg) : ")
  suhu = input_float("  - Suhu Tubuh (°C)              : ")
  waktu_donor_terakhir = input_int("  - Jarak dari donor terakhir (bln): ")

  alasan_gagal = analisis_kelayakan(
      usia, berat_badan, hb, sistol, diastol, suhu, waktu_donor_terakhir
  )

  lolos = len(alasan_gagal) == 0
  status_teks = "LOLOS" if lolos else "TIDAK LOLOS"
  catatan_teks = "Memenuhi syarat" if lolos else " ; ".join(alasan_gagal)

  # Simpan ke SQLite lokal dan perbarui file rekap_pendonor.txt
  simpan_pendonor({
      "nama": nama,
      "usia": usia,
      "berat_badan": berat_badan,
      "hb": hb,
      "sistol": sistol,
      "diastol": diastol,
      "suhu": suhu,
      "jarak_donor": waktu_donor_terakhir,
      "status": status_teks,
      "catatan": catatan_teks,
  })

  # Nomor urut terbaru diambil langsung dari jumlah data di database lokal
  no_urut = ambil_total_pendonor()
  waktu_cetak = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  # --- STRUK HASIL SKRINING ---
  print(f"\n{BIRU}{'='*80}{RESET}")
  print(
      f"{BOLD}{BIRU}                          STRUK HASIL SKRINING MEDIS"
      f"                       {RESET}"
  )
  print(f"{BIRU}{'='*80}{RESET}")
  print(f" No. Urut Data  : #{no_urut}")
  print(f" Waktu Input    : {waktu_cetak}")
  print(f" Nama Pendonor  : {nama.upper()}")
  print(f" Usia           : {usia} Tahun")
  print(f" Berat Badan    : {berat_badan} kg")
  print(f" Kadar Hb       : {hb} gr%")
  print(f" Tekanan Darah  : {sistol}/{diastol} mmHg")
  print(f" Suhu Tubuh     : {suhu} °C")
  print(f" Jarak Donor    : {waktu_donor_terakhir} bulan")
  print(f"{BIRU}{'-'*80}{RESET}")

  if lolos:
    print(f"{HIJAU}{BOLD} STATUS KELAYAKAN : LOLOS (MEMENUHI SYARAT){RESET}")
    print(
        f"{HIJAU} Keterangan       : Pendonor dapat dilanjutkan ke tahap"
        f" pengambilan darah (aftap) oleh petugas.{RESET}"
    )
  else:
    print(f"{MERAH}{BOLD} STATUS KELAYAKAN : TIDAK LOLOS (GAGAL){RESET}")
    print(f"{MERAH} Identifikasi Kondisi / Alasan Penolakan :{RESET}")
    for i, alasan in enumerate(alasan_gagal, 1):
      print(f"{MERAH}  {i}. {alasan}{RESET}")

  print(f"{BIRU}{'='*80}{RESET}\n")


# ----------------------------------------------------------------------------
# FUNGSI tampilkan_riwayat() & tampilkan_isi_txt()
# Membantu petugas melihat 10 riwayat terakhir atau melihat seluruh data
# yang tersimpan dalam format teks agar semuanya terlihat jelas.
# ----------------------------------------------------------------------------
def tampilkan_riwayat():
  rows = ambil_riwayat_terakhir(limit=10)
  print(f"\n{BIRU}{'='*80}{RESET}")
  print(
      f"{BOLD}{BIRU}                 RIWAYAT 10 PENDONOR TERAKHIR (DATABASE LOKAL)"
      f"                {RESET}"
  )
  print(f"{BIRU}{'='*80}{RESET}")

  if not rows:
    print(f" {KUNING}Belum ada data pendonor yang tersimpan.{RESET}")
  else:
    for row in rows:
      no_id, waktu, nama, status, catatan = row
      warna_status = HIJAU if status == "LOLOS" else MERAH
      print(f" #{no_id} | {waktu} | {BOLD}{nama}{RESET}")
      print(f"      Status  : {warna_status}{BOLD}{status}{RESET}")
      print(f"      Catatan : {catatan}")
      print(f" {BIRU}{'-'*76}{RESET}")

  print(f"{BIRU}{'='*80}{RESET}\n")


def tampilkan_isi_txt():
  """Memperbarui file .txt lalu mencetak seluruh isinya ke terminal."""
  export_semua_ke_txt()
  print(f"\n{BIRU}{'='*80}{RESET}")
  print(
      f"{BOLD}{BIRU}               SEMUA DATA TERDATA DALAM TEKS ({TXT_FILE})"
      f"              {RESET}"
  )
  print(f"{BIRU}{'='*80}{RESET}\n")

  with open(TXT_FILE, "r", encoding="utf-8") as f:
    isi = f.read()

  for baris in isi.splitlines():
    if "Status        : LOLOS" in baris:
      print(f"{HIJAU}{BOLD}{baris}{RESET}")
    elif "Status        : TIDAK LOLOS" in baris:
      print(f"{MERAH}{BOLD}{baris}{RESET}")
    else:
      print(baris)

  print(f"\n{BIRU}{'='*80}{RESET}\n")


# ----------------------------------------------------------------------------
# FUNGSI main()
# Berisi seluruh alur utama program dan menu interaktif.
# ----------------------------------------------------------------------------
def main():
  init_db()
  export_semua_ke_txt()

  while True:
    cetak_header()
    print(" Pilih menu:")
    print("  [1] Input & Skrining Calon Pendonor Baru")
    print("  [2] Lihat Rekap & 10 Riwayat Terakhir")
    print("  [3] Lihat Semua Data Lengkap (.txt)")
    print("  [4] Keluar")

    pilihan = input("\n Masukkan pilihan (1/2/3/4): ").strip()

    if pilihan == "1":
      while True:
        proses_skrining_baru()
        lanjut = (
            input("Apakah ingin memasukkan data pendonor lagi? (y/n): ")
            .strip()
            .lower()
        )
        if lanjut != "y":
          print(
              f"\n{KUNING}Sesi input selesai. Total keseluruhan pendonor"
              f" tersimpan: {ambil_total_pendonor()} orang.{RESET}\n"
          )
          break
        print("\n" * 2)
    elif pilihan == "2":
      tampilkan_riwayat()
      input("Tekan Enter untuk kembali ke menu...")
    elif pilihan == "3":
      tampilkan_isi_txt()
      input("Tekan Enter untuk kembali ke menu...")
    elif pilihan == "4":
      print(
          f"\n{KUNING}Program ditutup. Total keseluruhan pendonor tersimpan"
          f" di {DB_FILE}: {ambil_total_pendonor()} orang.{RESET}"
      )
      print(f"{BIRU}{'='*80}{RESET}")
      break
    else:
      print(
          f"\n{MERAH}[!] Pilihan tidak valid. Silakan pilih 1, 2, 3, atau"
          f" 4.{RESET}\n"
      )


# ----------------------------------------------------------------------------
# TITIK MASUK PROGRAM
# ----------------------------------------------------------------------------
if __name__ == "__main__":
  main()