# J5 独立复核包

先读 J5_hardcore_audit.md。两个可直接交给理论作者审查的补充文件是：

- J5_ceiling_proof.md：小 ground set 确定性 ceiling 的完整一般证明草稿、逐实例加强式及非负 slack 分解。
- J5_variant_certificates.md：双 submodular 实例核验、固定参数的 16 个有理对偶，以及 PE₁ 的两个小表形式的完整反例。

J5_source_manifest.json 锁定此次读取的 21 个远程源文件及其 Git blob 哈希。复现脚本本身不依赖仓库或网络。

## 运行

验证环境：Python 3.12.13、NumPy 2.3.5、SciPy 1.17.0、SymPy 1.14.0。已有这些库时直接执行：

    python3 J5_hardcore_oracles.py --output-dir reproduced

需要新建环境时：

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python J5_hardcore_oracles.py --output-dir reproduced

本次完整检查约 23 秒。运行时间随机器变化；每个 LP 设有 45 秒限制，任何非最优退出都使独立检查失败，不会被静默当作不可行。

脚本会写入新的 JSON 与 log。附带的原始 JSON 保存每个固定参数 LP 对偶的非零乘子、完整 PE₁ 有理函数值及正多项式的系数。JSON 内的数值 LP 表不等于任意参数的形式化证明；一般推导及其适用量词见两份证明补充。

PE₁ 的函数已固定为有理计数表，复现不要求求解器在有多个最优解时返回与本次相同的顶点。固定参数的双 submodular 对偶会重新求解后逐系数精确核对。

## 状态

[VERIFIED-SYMBOLIC]：列出的 14 个恒等式和非负系数证书。
[VERIFIED-LP]：52 个独立算法侧 LP、有限有理实例、16 个完整有理对偶和 PE₁ 终点穷举。
[HAND-PROOF-UNREVIEWED]：一般集合上的交换/求和、限制/补零、归纳及 minimax 量词装配。

仍开放：一般 $W_m$ 的匹配下界；一般 $K,R$ 的 PE 比较；有限 $n$ 的随机 minimax 精确值。此包没有修改远程论文源码。
