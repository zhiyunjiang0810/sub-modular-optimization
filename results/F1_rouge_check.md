# F1.1 — 自实现 ROUGE-1 F 与 `rouge-score` 的逐项核对

状态：**[VERIFIED-NUMERIC] 通过，无需修改 E3**。
脚本：`results/F1_rouge_check.py`；机器可读结果：`results/F1_rouge_check.json`。

## 1 安装（走代理）

`pip install rouge-score` 在系统 Python 上失败（Debian 打过补丁的 setuptools 在构建该 sdist 时抛
`AttributeError: install_layout`，与网络无关：包已经下载成功）。改用干净 venv 安装成功：

```
python3 -m venv <venv>
<venv>/bin/pip install --upgrade pip setuptools wheel
<venv>/bin/pip install rouge-score          # rouge-score 0.1.2, nltk 3.10.3, absl-py 2.5.0
<venv>/bin/python results/F1_rouge_check.py
```

`rouge_scorer.RougeScorer(['rouge1'], use_stemmer=False)`，即默认不做 stemming（与 E3 一致）。

## 2 对比设计

- 语料：BBC 三个类别 `business` / `sport` / `tech`，**每类前 30 篇有参考摘要且句数 ≥ 5 的文章**，
  共 90 篇。文章读取、句子切分、参考摘要获取全部**直接 import `results/E3_run.py` 的函数**
  （`read_text` / `split_sentences` / `get_reference` / `tokens` / `Rouge1F`），没有另写一份管线。
- 候选摘要集合（两边打的是**同一批**子集）：每篇取
  前 `min(n,10)` 个单句 `{i}`、前缀 `{0..K-1}`（K=1..5）、以及 E3 的 greedy-on-f 前缀（K=1..5），
  去重后共 1,624 个 (文章, 子集) 对。
- 我方：`Rouge1F(sent_counts, sent_len, ref_counts, ref_len)(S)`（集合形式，与 E3 逐位相同的调用）。
  对方：`scorer.score(reference, ' '.join(选中句子))['rouge1'].fmeasure`。

## 3 结果

| 量 | 值 |
|---|---|
| 文章数 | 90（business/sport/tech 各 30） |
| 比较次数 | 1,624 |
| **最大绝对差** | **0.0**（精确的 0，不是 1e-16） |
| **平均绝对差** | **0.0** |
| 中位绝对差 | 0.0 |
| 绝对差 > 1e-6 的比较数 | 0 / 1,624 |
| 参考摘要 token 序列不一致的文章数 | 0 / 90 |
| 参考摘要 token 总数（我方 / 对方） | 14,029 / 14,029 |

因为差 = 0 < 1e-6，**没有改 `results/E3_run.py` 的 `Rouge1F`，也没有因此重跑 E3**
（E3 因 F1.3 的新统计列另行重跑了一次，见 `F1_fixes.md`，那次重跑的 ratio / η^sel / η^path /
sign-viol 与旧 CSV 逐行完全一致）。

## 4 为什么恰好为 0：两个 tokenizer 在这批语料上重合

两边的公式本来就一样（clipped unigram overlap，P = overlap/|cand|，R = overlap/|ref|，
F = 2PR/(P+R)，空则 0），唯一可能的差别在 tokenization：

- 我方：`re.compile(r'\w+').findall(text.lower())` —— Unicode `\w`，保留下划线与带重音字母。
- `rouge_score`：`text.lower()` → `re.sub(r'[^a-z0-9]+', ' ', text)` → 按空白切 → 只保留
  匹配 `^[a-z0-9]+$` 的 token。会把下划线切开、把带重音字母拆碎。

这两者**在一般文本上确实不同**（负控制，跑在同一对比函数上）：

| reference | candidate | 我方 F | rouge-score F | 差 |
|---|---|---|---|---|
| `the café visit was fine` | `a café visit` | 0.5000000000 | 0.5000000000 | 0（本例恰好抵消） |
| `under_score token here` | `under_score token` | 0.8000000000 | 0.8571428571 | 5.7e-2 |
| `naive naïve resume résumé` | `naïve résumé` | 0.6666666667 | 0.8000000000 | 1.3e-1 |
| `Zurich Zürich Beyoncé` | `Zürich Beyoncé` | 0.8000000000 | 0.8571428571 | 5.7e-2 |

（`tokens('Zurich Zürich Beyoncé') = ['zurich','zürich','beyoncé']`，
`rouge_score` 给 `['zurich','z','rich','beyonc']`。）所以对比装置**有能力**发现差异。

而这 90 篇文章的实测：把 90 篇的**全部句子加参考摘要**共 1,608 段文本逐段比对，
`E3.tokens(s) == rouge_score.tokenize(s, None)` 的比例是 **1,608 / 1,608**；
统计"匹配 `\w` 但不在 `[A-Za-z0-9]` 内的字符"（即两个 tokenizer 会分歧的字符）出现次数为 **0**：
这批 BBC 文本里没有下划线、没有带重音字母。英镑符号 `£` 两边都不是词字符，同样被丢弃。
因此两个 tokenizer 给出逐 token 相同的序列，公式又相同，F 值精确相等。

## 5 诚实的边界

1. 差为 0 是**这批语料**（3 类 × 30 篇）的性质，不是两个实现等价的证明。E3 全量用的是每类 100 篇，
   若某篇含重音字母或下划线，两者会分叉（第 4 节的量级：单篇 F 可差 0.05–0.13）。
   已做的检查只覆盖了 90 篇 × 1,624 个子集。
2. 未核对 ROUGE-2 / ROUGE-L：E3 的 f 只用 ROUGE-1 F，其他类型不在管线里。
3. `use_stemmer=False`：E3 明确不做 stemming，`rouge_score` 的默认也是不 stem，两边一致；
   若改成 `use_stemmer=True`（Porter，仅对长度 > 3 的词）差异会立刻出现，这不是本次核对的对象。
4. 句子切分（`split_sentences`）是 E3 自己的，`rouge_score` 不涉及句子切分，本次对比让两边用
   同一批已经切好的句子，所以切分的已知缺陷（缩写词过切）不在此项核验范围内。
