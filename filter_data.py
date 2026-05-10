from pathlib import Path

import pandas as pd

# ======================
# 1. Baca file CSV asli
# ======================
file_path = "data.csv"
out_path = "data_filtered.csv"

raw = pd.read_csv(file_path, header=None, dtype=str, encoding="utf-8-sig")

# ======================
# 2. Ambil metadata tahun & bulan
# ======================
tahun = raw.iloc[1].ffill()
bulan = raw.iloc[2]

metadata = pd.DataFrame({"tahun": tahun, "bulan": bulan})

# ======================
# 3. Filter: hanya kolom yang bukan "Tahunan" dan tahun <= 2025
# ======================
kolom_valid = (
    metadata["bulan"].notna()
    & (metadata["bulan"] != "Tahunan")
    & (metadata["tahun"].notna())
    & (
        pd.to_numeric(
            metadata["tahun"].astype(str).str.strip().str[:4], errors="coerce"
        )
        <= 2025
    )
)

# Kolom 0 (nama pintu masuk) selalu disimpan
kolom_dipakai = [0] + metadata.index[kolom_valid].tolist()

# ======================
# 4. Potong data
# ======================
df_filtered = raw.iloc[:, kolom_dipakai].copy()

# Ganti "-" dengan "0"
df_filtered = df_filtered.replace("-", "0")

# ======================
# 5. Simpan hasil
# ======================
df_filtered.to_csv(out_path, index=False, header=False, encoding="utf-8-sig")

print(f"Data difilter dan disimpan ke: {out_path}")
print(f"Jumlah kolom sebelum: {raw.shape[1]}")
print(f"Jumlah kolom sesudah: {df_filtered.shape[1]}")
