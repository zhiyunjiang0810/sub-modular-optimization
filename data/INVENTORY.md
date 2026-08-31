# data/INVENTORY.md — 数据集清单（2026-08-31 整理）

每个数据集一行：文件名、规模、来源、是否进 git。所有文件均低于 20MB（zip 规则）/ 50MB（单文件规则）阈值，**全部进 git，无 .gitignore 排除项**。

| 数据集 / 文件 | 规模 | 来源 | 进 git |
|---|---|---|---|
| `data/airline.csv` | 2.9 MB，25,977 行 | 用户上传（原仓库根目录，本次移入 data/） | 是 |
| `data/bbc/`（BBC News Summary，含 News Articles + Summaries 各 5 类目：business/entertainment/politics/sport/tech，2,343 个 txt；另有 bbc.classes/.docs/.mtx/.terms 词项矩阵） | 14 MB，2,356 个文件 | 用户上传的 bbc.zip 解压 | 是 |
| `data/raw/bbc.zip`（原始 zip） | 3.7 MB（< 20 MB，按规则保留） | 用户上传 | 是 |
| `data/graphs/facebook_gemsec/artist_edges.csv` | 9.0 MB；n=50,515，m=819,306（无向） | SNAP GEMSEC Facebook page-page: https://snap.stanford.edu/data/gemsec-Facebook.html（原实验的 artist edges 即出自此处） | 是 |
| `data/graphs/facebook_gemsec/politician_edges.csv` | 393 KB；n=5,908，m=41,729（无向） | 同上 | 是 |
| `data/graphs/facebook_gemsec/government_edges.csv` | 845 KB；n=7,057，m=89,455（无向） | 同上 | 是 |
| `data/graphs/email_eu_core/email-Eu-core.txt`（+ department-labels） | 245 KB；n=1,005，m=25,571（有向，含自环） | SNAP: https://snap.stanford.edu/data/email-Eu-core.html | 是 |
| `data/raw/gemsec_facebook_dataset.tar.gz`（GEMSEC 全部 8 类目原始包） | 4.9 MB | https://snap.stanford.edu/data/gemsec_facebook_dataset.tar.gz | 是 |
| `data/raw/email-Eu-core.txt.gz`、`email-Eu-core-department-labels.txt.gz` | 78 KB + 2.6 KB | https://snap.stanford.edu/data/email-Eu-core.txt.gz 、…-department-labels.txt.gz | 是 |

## 重新下载命令（如需）

```bash
curl -sSL -O https://snap.stanford.edu/data/gemsec_facebook_dataset.tar.gz
curl -sSL -O https://snap.stanford.edu/data/email-Eu-core.txt.gz
curl -sSL -O https://snap.stanford.edu/data/email-Eu-core-department-labels.txt.gz
```
（注意：SNAP 页面上曾出现过的 `facebook_clean_data.zip` 文件名现已 404，tar.gz 是当前有效链接。）

## 缺失与替代记录

- **旧的 Twitter / reddit 社交网络图原始文件已丢失，无法恢复。** 论文实验将改用上述公开替代图：
  GEMSEC Facebook page-page 的 artist（与原实验同源）、politician、government 三个类目，
  以及 email-Eu-core。论文中的数据集描述与引用需相应更新：图数据引用改为
  Rozemberczki et al., GEMSEC (SNAP) 与 Leskovec et al., email-Eu-core (SNAP)
  [CITATION-NEEDS-VERIFICATION：作者与年份需在定稿时核对 SNAP 页面给出的引用格式]。
- **`legacy/SubModular.ipynb` 缺失**：全仓库未找到该文件，仅有记录，待用户补传。
- `legacy/airline_performance.py`：文件原在仓库根目录（用户上传），本次移入 `legacy/`。
- `airline_eta.py`（根目录）：用户上传，未在本次整理指令范围内，保留原位。
- `data`（1 字节占位文件）：GitHub 网页 "Create data" 生成的空文件，已删除并替换为 `data/` 目录。
