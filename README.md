py2/README.md
```

```markdown
# Plot Wisman - Visualisasi Kunjungan Wisatawan Mancanegara

## Sumber Data

- **File input:** `data.csv`
- **Data:** Kunjungan wisatawan mancanegara (wisman) ke Indonesia berdasarkan pintu masuk
- **Periode data:** Januari 2008 - Desember 2025
- **Pintu Masuk yang dianalisis:**
  - A. Pintu Udara
  - B. Pintu Laut
  - C. Pintu Darat

---

## Daftar Plot yang Dihasilkan

### Plot 01 & 02 - Perbandingan 3 Pintu Masuk
| File | Deskripsi |
|------|-----------|
| `01_per_pintu_2018_2020.png` | Kunjungan wisman per pintu masuk (Udara, Laut, Darat) dari Jan 2018 - Des 2020 |
| `02_per_pintu_2023_2025.png` | Kunjungan wisman per pintu masuk (Udara, Laut, Darat) dari Jan 2023 - Des 2025 |

### Plot 03 & 04 - Total Kunjungan per Tahun
| File | Deskripsi |
|------|-----------|
| `03_total_2019.png` | Total kunjungan wisman 3 pintu masuk sepanjang tahun 2019 |
| `04_total_2025.png` | Total kunjungan wisman 3 pintu masuk sepanjang tahun 2025 |

### Plot 05 - Perbandingan Dua Tahun
| File | Deskripsi |
|------|-----------|
| `05_total_2019_vs_2025.png` | Perbandingan total kunjungan wisman tahun 2019 vs 2025 per bulan |

### Plot 06 & 07 - Total + 3 Pintu Masuk
| File | Deskripsi |
|------|-----------|
| `06_total_dengan_pintu_2019.png` | Total + 3 pintu masuk wisman tahun 2019 (4 garis) |
| `07_total_dengan_pintu_2025.png` | Total + 3 pintu masuk wisman tahun 2025 (4 garis) |

### Plot 08-12 - Data 2008-2025 (Periode Panjang)
| File | Deskripsi |
|------|-----------|
| `08_total_2008_2025.png` | Total semua kunjungan wisman dari Jan 2008 - Des 2025 |
| `09_pintu_udara_2008_2025.png` | Kunjungan wisman via Pintu Udara dari Jan 2008 - Des 2025 |
| `10_pintu_laut_2008_2025.png` | Kunjungan wisman via Pintu Laut dari Jan 2008 - Des 2025 |
| `11_pintu_darat_2008_2025.png` | Kunjungan wisman via Pintu Darat dari Jan 2008 - Des 2025 |
| `12_semua_pintu_2008_2025.png` | Perbandingan 3 pintu masuk (Udara, Laut, Darat) dari Jan 2008 - Des 2025 |

### Plot 13 - Detail 2023-2025
| File | Deskripsi |
|------|-----------|
| `13_per_pintu_2023_2025.png` | Kunjungan wisman per pintu masuk dari Jan 2023 - Des 2025 |

---

## Warna Setiap Pintu Masuk

| Pintu Masuk | Warna |
|-------------|-------|
| A. Pintu Udara | Biru (`#1f77b4`) |
| B. Pintu Laut | Oranye (`#ff7f0e`) |
| C. Pintu Darat | Hijau (`#2ca02c`) |
| Total | Merah (`#d62728`) |

---

## Cara Menjalankan

```bash
python main.py
```

Plot akan disimpan di folder `plot_wisman_outputs/`.