from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator

# ======================
# 1. Baca file CSV
# ======================
file_path = "data.csv"
out_dir = Path("plot_wisman_outputs")
out_dir.mkdir(parents=True, exist_ok=True)

raw = pd.read_csv(file_path, header=None, dtype=str, encoding="utf-8-sig")

# ======================
# 2. Ambil metadata tahun & bulan
# ======================
tahun = raw.iloc[1].ffill()
bulan = raw.iloc[2]

metadata = pd.DataFrame({"tahun": tahun, "bulan": bulan})

kolom_bukan_tahunan = (
    metadata["tahun"].notna()
    & metadata["bulan"].notna()
    & (metadata["bulan"] != "Tahunan")
)

kolom_dipakai = [0] + metadata.index[kolom_bukan_tahunan].tolist()
df = raw.iloc[3:, kolom_dipakai].copy()

# ======================
# 3. Rename kolom
# ======================
nama_kolom = ["Pintu Masuk"]
for idx in metadata.index[kolom_bukan_tahunan]:
    nama_kolom.append(f"{metadata.loc[idx, 'tahun']}-{metadata.loc[idx, 'bulan']}")

df.columns = nama_kolom
df["Pintu Masuk"] = df["Pintu Masuk"].astype(str).str.strip()

# ======================
# 4. Bersihkan angka
# ======================
kolom_nilai = df.columns[1:]
df[kolom_nilai] = (
    df[kolom_nilai]
    .replace("-", pd.NA)
    .replace("", pd.NA)
    .apply(pd.to_numeric, errors="coerce")
)

# ======================
# 5. Ambil row yang ingin diplot
# ======================
rows_plot = ["A. Pintu Udara", "B. Pintu Laut", "C. Pintu Darat"]
df_plot = df[df["Pintu Masuk"].isin(rows_plot)].copy()
plot_data = df_plot.set_index("Pintu Masuk").T
plot_data = plot_data[[c for c in rows_plot if c in plot_data.columns]]

# ======================
# 6. Ubah index menjadi datetime
# ======================
bulan_map = {
    "Januari": "01",
    "Februari": "02",
    "Maret": "03",
    "April": "04",
    "Mei": "05",
    "Juni": "06",
    "Juli": "07",
    "Agustus": "08",
    "September": "09",
    "Oktober": "10",
    "November": "11",
    "Desember": "12",
}

tanggal = plot_data.index.to_series().str.split("-", n=1, expand=True)
plot_data.index = pd.to_datetime(
    tanggal[0] + "-" + tanggal[1].map(bulan_map) + "-01", errors="coerce"
)

plot_data = plot_data[plot_data.index.notna()].sort_index()

# Batas maksimum hanya sampai 2025, tidak memakai data 2026
plot_data = plot_data.loc[plot_data.index <= "2025-12-31"]

# ======================
# 7. Konfigurasi warna dan axis
# ======================
warna_pintu = {
    "A. Pintu Udara": "#1f77b4",
    "B. Pintu Laut": "#ff7f0e",
    "C. Pintu Darat": "#2ca02c",
}

nama_bulan_pendek = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agu",
    "Sep",
    "Okt",
    "Nov",
    "Des",
]


def fmt_kunjungan(x, pos):
    x = float(x)
    if x >= 1_000_000:
        return f"{x / 1_000_000:.1f}M"
    return f"{int(x / 1_000)}K"


def setup_y_axis(ax, data, step=200_000):
    max_val = pd.to_numeric(
        data.stack() if isinstance(data, pd.DataFrame) else data, errors="coerce"
    ).max()
    if pd.isna(max_val):
        max_val = step
    ymax = ((int(max_val) // step) + 1) * step
    ax.set_ylim(0, ymax)
    ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_kunjungan))


def save_per_pintu(data, start, end, title, filename):
    subset = data.loc[start:end].dropna(how="all", axis=0)
    fig, ax = plt.subplots(figsize=(14, 6))

    for col in subset.columns:
        ax.plot(
            subset.index,
            subset[col],
            marker="o",
            linewidth=1.8,
            label=col,
            color=warna_pintu.get(col),
        )

    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Kunjungan")
    ax.grid(True, alpha=0.3)
    ax.legend()

    setup_y_axis(ax, subset, step=200_000)

    tick_idx = subset.index[::3]
    ax.set_xticks(list(tick_idx))
    ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(out_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_total_year(data, year, filename):
    subset = data.loc[f"{year}-01-01" : f"{year}-12-31"].copy()
    total = subset.sum(axis=1, skipna=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        pd.Index(nama_bulan_pendek[: len(total)]),
        total.values,
        marker="o",
        linewidth=2,
        label=f"Total {year}",
    )

    ax.set_title(
        f"Total Kunjungan Wisman 3 Pintu Masuk Tahun {year}", fontsize=14, weight="bold"
    )
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Kunjungan")
    ax.grid(True, alpha=0.3)
    ax.legend()

    setup_y_axis(ax, total, step=200_000)

    plt.tight_layout()
    plt.savefig(out_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_total_year_with_doors(data, year, filename):
    subset = data.loc[f"{year}-01-01" : f"{year}-12-31"].dropna(how="all", axis=0)
    total = subset.sum(axis=1, skipna=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot total
    ax.plot(
        nama_bulan_pendek[: len(subset)],
        total.values,
        marker="o",
        linewidth=2.5,
        label="Total",
        color="#d62728",
    )

    # Plot per door
    for col in subset.columns:
        ax.plot(
            nama_bulan_pendek[: len(subset)],
            subset[col].values,
            marker="o",
            linewidth=1.8,
            label=col,
            color=warna_pintu.get(col),
        )

    ax.set_title(
        f"Kunjungan Wisman Total & per Pintu Masuk Tahun {year}",
        fontsize=14,
        weight="bold",
    )
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Kunjungan")
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Use combined data for y-axis scale
    combined = pd.concat([total, subset.stack()])
    setup_y_axis(ax, combined, step=200_000)

    plt.tight_layout()
    plt.savefig(out_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_compare_total_years(data, year_a, year_b, filename):
    total_a = data.loc[f"{year_a}-01-01" : f"{year_a}-12-31"].sum(axis=1, skipna=True)
    total_b = data.loc[f"{year_b}-01-01" : f"{year_b}-12-31"].sum(axis=1, skipna=True)

    compare = pd.DataFrame(
        {
            str(year_a): total_a.values,
            str(year_b): total_b.values,
        },
        index=pd.Index(nama_bulan_pendek),
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        pd.Index(compare.index),
        compare[str(year_a)],
        marker="o",
        linewidth=2,
        label=str(year_a),
    )
    ax.plot(
        pd.Index(compare.index),
        compare[str(year_b)],
        marker="o",
        linewidth=2,
        label=str(year_b),
    )

    ax.set_title(
        f"Perbandingan Total Kunjungan Wisman {year_a} vs {year_b}",
        fontsize=14,
        weight="bold",
    )
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Kunjungan")
    ax.grid(True, alpha=0.3)
    ax.legend()

    setup_y_axis(ax, compare, step=200_000)

    plt.tight_layout()
    plt.savefig(out_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ======================
# 8. Buat semua plot
# ======================
# --- Plot 01-02: Per Pintu (2018-2020 & 2023-2025) ---
save_per_pintu(
    plot_data,
    "2018-01-01",
    "2020-12-31",
    "Kunjungan Wisman per Pintu Masuk: Jan 2018 - Des 2020",
    "01_per_pintu_2018_2020.png",
)

save_per_pintu(
    plot_data,
    "2023-01-01",
    "2025-12-31",
    "Kunjungan Wisman per Pintu Masuk: Jan 2023 - Des 2025",
    "02_per_pintu_2023_2025.png",
)

# --- Plot 03-04: Total per tahun (2019 & 2025) ---
save_total_year(plot_data, 2019, "03_total_2019.png")
save_total_year(plot_data, 2025, "04_total_2025.png")

# --- Plot 05: Perbandingan total 2019 vs 2025 ---
save_compare_total_years(plot_data, 2019, 2025, "05_total_2019_vs_2025.png")

# --- Plot 06-07: Total + 3 pintu per tahun ---
save_total_year_with_doors(plot_data, 2019, "06_total_dengan_pintu_2019.png")
save_total_year_with_doors(plot_data, 2025, "07_total_dengan_pintu_2025.png")

# ======================
# 9. Plot terpisah 2008-2025
# ======================
total_all = plot_data.sum(axis=1)

# --- Plot 08: Total semua wisman ---
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(
    plot_data.index,
    total_all.values,
    marker="o",
    linewidth=2,
    color="#d62728",
    label="Total Wisman",
)
ax.set_title("Total Kunjungan Wisman 2008-2025", fontsize=14, weight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
setup_y_axis(ax, total_all, step=200_000)
tick_idx = plot_data.index[::6]
ax.set_xticks(list(tick_idx))
ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(out_dir / "08_total_2008_2025.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 09: Pintu Udara ---
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(
    plot_data.index,
    plot_data["A. Pintu Udara"].values,
    marker="o",
    linewidth=2,
    color="#1f77b4",
    label="A. Pintu Udara",
)
ax.set_title("Kunjungan Wisman via Pintu Udara 2008-2025", fontsize=14, weight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
setup_y_axis(ax, plot_data["A. Pintu Udara"], step=100_000)
tick_idx = plot_data.index[::6]
ax.set_xticks(list(tick_idx))
ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(out_dir / "09_pintu_udara_2008_2025.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 10: Pintu Laut ---
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(
    plot_data.index,
    plot_data["B. Pintu Laut"].values,
    marker="o",
    linewidth=2,
    color="#ff7f0e",
    label="B. Pintu Laut",
)
ax.set_title("Kunjungan Wisman via Pintu Laut 2008-2025", fontsize=14, weight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
setup_y_axis(ax, plot_data["B. Pintu Laut"], step=100_000)
tick_idx = plot_data.index[::6]
ax.set_xticks(list(tick_idx))
ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(out_dir / "10_pintu_laut_2008_2025.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 11: Pintu Darat ---
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(
    plot_data.index,
    plot_data["C. Pintu Darat"].values,
    marker="o",
    linewidth=2,
    color="#2ca02c",
    label="C. Pintu Darat",
)
ax.set_title("Kunjungan Wisman via Pintu Darat 2008-2025", fontsize=14, weight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
setup_y_axis(ax, plot_data["C. Pintu Darat"], step=100_000)
tick_idx = plot_data.index[::6]
ax.set_xticks(list(tick_idx))
ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(out_dir / "11_pintu_darat_2008_2025.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 12: Semua pintu together ---
fig, ax = plt.subplots(figsize=(16, 7))
for col in plot_data.columns:
    ax.plot(
        plot_data.index,
        plot_data[col].values,
        marker="o",
        linewidth=1.8,
        label=col,
        color=warna_pintu.get(col),
    )
ax.set_title("Kunjungan Wisman per Pintu Masuk 2008-2025", fontsize=14, weight="bold")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
setup_y_axis(ax, plot_data, step=100_000)
tick_idx = plot_data.index[::6]
ax.set_xticks(list(tick_idx))
ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(out_dir / "12_semua_pintu_2008_2025.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 15: 3 subplots (Udara, Laut, Darat) dalam 1 figure ---
fig, axes = plt.subplots(3, 1, figsize=(16, 16))

doors = [
    ("A. Pintu Udara", "#1f77b4"),
    ("B. Pintu Laut", "#ff7f0e"),
    ("C. Pintu Darat", "#2ca02c"),
]

for ax, (col, color) in zip(axes, doors):
    ax.plot(
        plot_data.index,
        plot_data[col].values,
        marker="o",
        linewidth=2,
        color=color,
        label=col,
    )
    ax.set_title(f"Kunjungan Wisman via {col} 2008-2025", fontsize=12, weight="bold")
    ax.set_ylabel("Jumlah Kunjungan")
    ax.grid(True, alpha=0.3)
    ax.legend()
    setup_y_axis(ax, plot_data[col], step=100_000)
    # Add padding at top and bottom of each subplot
    ylim = ax.get_ylim()
    ax.set_ylim(ylim[0], ylim[1] * 1.15)
    tick_idx = plot_data.index[::6]
    ax.set_xticks(list(tick_idx))
    ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")

axes[-1].set_xlabel("Bulan")
plt.subplots_adjust(hspace=0.35, top=0.95, bottom=0.08)
plt.savefig(out_dir / "15_subplots_pintu_2008_2025.png", dpi=600, bbox_inches="tight")
plt.close(fig)

# --- Plot 13: Semua pintu 2023-2025 ---
subset_2023 = plot_data.loc["2023-01-01":"2025-12-31"].dropna(how="all", axis=0)
fig, ax = plt.subplots(figsize=(14, 7))
for col in subset_2023.columns:
    ax.plot(
        subset_2023.index,
        subset_2023[col].values,
        marker="o",
        linewidth=2,
        label=col,
        color=warna_pintu.get(col),
    )
ax.set_title(
    "Kunjungan Wisman per Pintu Masuk: Jan 2023 - Des 2025", fontsize=14, weight="bold"
)
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
setup_y_axis(ax, subset_2023, step=100_000)
tick_idx = subset_2023.index[::3]
ax.set_xticks(list(tick_idx))
ax.set_xticklabels([d.strftime("%b %Y") for d in tick_idx], rotation=45, ha="right")
plt.tight_layout()
plt.savefig(out_dir / "13_per_pintu_2023_2025.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 14: Perbandingan tahun 2018, 2019, 2023, 2024, 2025 ---
tahun_list = [2018, 2019, 2023, 2024, 2025]
warna_tahun = {
    2018: "#1f77b4",
    2019: "#ff7f0e",
    2023: "#2ca02c",
    2024: "#d62728",
    2025: "#9467bd",
}

fig, ax = plt.subplots(figsize=(14, 7))
for year in tahun_list:
    yearly = plot_data.loc[f"{year}-01-01" : f"{year}-12-31"].sum(axis=1, skipna=True)
    ax.plot(
        nama_bulan_pendek[: len(yearly)],
        yearly.values,
        marker="o",
        linewidth=2,
        label=str(year),
        color=warna_tahun[year],
    )

ax.set_title(
    "Perbandingan Total Kunjungan Wisman 2018, 2019, 2023, 2024, 2025",
    fontsize=14,
    weight="bold",
)
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_ylim(0, 2_000_000)
ax.yaxis.set_major_locator(MultipleLocator(200_000))
ax.yaxis.set_major_formatter(FuncFormatter(fmt_kunjungan))

plt.tight_layout()
plt.savefig(out_dir / "14_perbandingan_tahun.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# ======================
# 10. Plot yearly aggregation (x-axis = year only) 2008-2025
# ======================

# Aggregate data by year
yearly_total = plot_data.sum(axis=1).resample("YE").sum()
yearly_udara = plot_data["A. Pintu Udara"].resample("YE").sum()
yearly_laut = plot_data["B. Pintu Laut"].resample("YE").sum()
yearly_darat = plot_data["C. Pintu Darat"].resample("YE").sum()
yearly_all = plot_data.resample("YE").sum()

years = yearly_total.index.year.tolist()
year_labels = [str(y) for y in years]

# --- Plot 16: Total per tahun ---
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(
    year_labels,
    yearly_total.values,
    marker="o",
    linewidth=2.5,
    color="#d62728",
    label="Total Wisman",
)
ax.set_title("Total Kunjungan Wisman per Tahun 2008-2025", fontsize=14, weight="bold")
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_ylim(0, 2_000_000)
ax.yaxis.set_major_locator(MultipleLocator(200_000))
ax.yaxis.set_major_formatter(FuncFormatter(fmt_kunjungan))
plt.xticks(year_labels)
plt.tight_layout()
plt.savefig(out_dir / "16_total_per_tahun.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 17: Pintu Udara per tahun ---
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(
    year_labels,
    yearly_udara.values,
    marker="o",
    linewidth=2.5,
    color="#1f77b4",
    label="A. Pintu Udara",
)
ax.set_title(
    "Kunjungan Wisman via Pintu Udara per Tahun 2008-2025", fontsize=14, weight="bold"
)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_ylim(0, 2_000_000)
ax.yaxis.set_major_locator(MultipleLocator(200_000))
ax.yaxis.set_major_formatter(FuncFormatter(fmt_kunjungan))
plt.xticks(year_labels)
plt.tight_layout()
plt.savefig(out_dir / "17_pintu_udara_per_tahun.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 18: Pintu Laut per tahun ---
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(
    year_labels,
    yearly_laut.values,
    marker="o",
    linewidth=2.5,
    color="#ff7f0e",
    label="B. Pintu Laut",
)
ax.set_title(
    "Kunjungan Wisman via Pintu Laut per Tahun 2008-2025", fontsize=14, weight="bold"
)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_ylim(0, 2_000_000)
ax.yaxis.set_major_locator(MultipleLocator(200_000))
ax.yaxis.set_major_formatter(FuncFormatter(fmt_kunjungan))
plt.xticks(year_labels)
plt.tight_layout()
plt.savefig(out_dir / "18_pintu_laut_per_tahun.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# --- Plot 19: Semua pintu per tahun ---
fig, ax = plt.subplots(figsize=(16, 7))
for col, color in zip(plot_data.columns, ["#1f77b4", "#ff7f0e", "#2ca02c"]):
    yearly_col = plot_data[col].resample("YE").sum()
    ax.plot(
        year_labels,
        yearly_col.values,
        marker="o",
        linewidth=2.5,
        label=col,
        color=color,
    )
ax.set_title(
    "Kunjungan Wisman per Pintu Masuk per Tahun 2008-2025", fontsize=14, weight="bold"
)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Kunjungan")
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_ylim(0, 2_000_000)
ax.yaxis.set_major_locator(MultipleLocator(200_000))
ax.yaxis.set_major_formatter(FuncFormatter(fmt_kunjungan))
plt.xticks(year_labels)
plt.tight_layout()
plt.savefig(out_dir / "19_semua_pintu_per_tahun.png", dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Plot berhasil disimpan di folder: {out_dir.resolve()}")
