# J5：用交换条件与并集误差闭合小 ground set 的确定性天花板

审查基准：GitHub `e83eacd4e6d5d896b9243e12165cba8e74c8b7d9`，2026-09-07。

**状态分开记录。** 下述三条核心分解为 `[VERIFIED-SYMBOLIC]`，独立脚本 `J5_hardcore_oracles.py`；52 个全格点算法侧 LP 为 `[VERIFIED-LP]`。一般集合上的交换、望远镜求和与 minimax 量词装配保留 `[HAND-PROOF-UNREVIEWED]`。这里给出完整一般证明草稿，已不再停在 H-E 原来的交集卡点；不把有限 LP 检查称作任意规模的机器证明。

## 1. 可替换的完整陈述

设 \(2\le K\le n\)，\(f(\varnothing)=\tilde f(\varnothing)=0\)，\(f\) 单调 submodular，且所有单元素边际满足

\[
\frac{d_e(A)}{u}\le\tilde d_e(A)\le o\,d_e(A),
\qquad u,o\ge1,\quad\eta=uo.
\]

算法只能查询 \(\tilde f\)，输出大小至多为 \(K\) 的集合。以 \(f(O)>0\) 的实例定义近似比。允许不限次数查询的**确定性 minimax 值**的候选完整定理为

\[
\boxed{C^*_{n,K}(\eta)
=\frac{K}{K+(\eta-1)\min\{K,n-K\}}.}
\]

算法侧由穷举全部 \(K\)-子集的预测最优解

\[
S\in\arg\max_{|T|=K}\tilde f(T)
\]

达到。对手侧由线性预测与 modular 真实目标达到。特别地，

\[
C^*_{n,K}(\eta)=
\begin{cases}
\displaystyle\frac{K}{(2K-n)+(n-K)\eta},&K\le n\le2K,\\[4pt]
1/\eta,&n\ge2K.
\end{cases}
\]

这里“算法侧下界”的量词是**存在算法，对所有合法实例均保证该值**。不是任意算法都保证该值。预测函数不需要 submodular。结论只依赖乘积，但覆盖每一种允许的拆分 \((u,o)\)。

## 2. 更强的逐实例结论

令 \(O\) 为一个大小恰为 \(K\) 的真实最优解，记

\[
a=|O\setminus S|,\quad A=f(S),\quad B=f(O),\quad
U=S\cup O,\quad Z=f(U).
\]

单调性允许把最优解补足到 \(K\)。将得到

\[
\boxed{B\le\left(1+\frac{(\eta-1)a}{K}\right)A.}\tag{1}
\]

随后只用 \(a\le\min\{K,n-K\}\)，就得到上一节的算法保证。无需假设 \(S\) 与 \(O\) 恰好最小重叠；重叠更多时，式 (1) 反而更强。

### 第一步：把所有交换条件加起来

对每个 \(s\in S\) 定义末端删除损失

\[
r_s=f(S)-f(S\setminus\{s\}),\qquad R=\sum_{s\in S}r_s.
\]

沿任意顺序加入 \(S\) 的元素，每一步的增加量至少是该元素的末端删除损失，因此

\[
0\le R\le A.\tag{2}
\]

对 \(b\in O\setminus S\)，记 \(D_b=d_b(S)\)。由于 \(S\) 在所有 \(K\)-集合中预测最优，对于**所有** \(s\in S\)，

\[
\tilde f(S)\ge\tilde f(S\setminus\{s\}\cup\{b\}),
\]

即

\[
\tilde d_b(S\setminus\{s\})
\le\tilde d_s(S\setminus\{s\}).
\]

结合真实目标的 diminishing returns 与两侧误差带，

\[
D_b\le d_b(S\setminus\{s\})
\le u\,\tilde d_b(S\setminus\{s\})
\le u\,\tilde d_s(S\setminus\{s\})
\le\eta r_s.\tag{3}
\]

令 \(D=\sum_{b\in O\setminus S}D_b\)。对全部 \(aK\) 对 \((b,s)\) 求和：

\[
KD\le\eta aR\le\eta aA.\tag{4}
\]

这里的关键是：删除端使用 \(S\) 的全部 \(K\) 个元素，包括交集中的元素。不是只在 \(S\setminus O\) 中配对交换。

由 submodularity 对并集增加量求和，

\[
Z-A\le D,
\qquad
Z\le\left(1+\frac{\eta a}{K}\right)A.\tag{5}
\]

### 第二步：在同一个并集上耦合两条误差带

令

\[
X=\tilde f(U)-\tilde f(S),\qquad
Y=\tilde f(U)-\tilde f(O).
\]

预测最优性给出 \(X\le Y\)。沿两条加入元素的链将单元素带望远镜相加，得到

\[
\frac{Z-A}{u}\le X\le Y\le o(Z-B).
\]

于是

\[
B\le\left(1-\frac1\eta\right)Z+\frac A\eta.\tag{6}
\]

这一步使用同一个预测集合函数在 \(S,O,U\) 上的值。它不要求 \(\tilde f\) submodular，也不要求算法实际查询 \(U\)。全局误差带保证这个未查询的并集仍受约束。

### 第三步：消去并集价值

在式 (6) 中代入式 (5)，使用 \(\eta\ge1\)：

\[
\begin{aligned}
B
&\le\left(1-\frac1\eta\right)
\left(1+\frac{\eta a}{K}\right)A+\frac A\eta\\
&=\left(1+\frac{(\eta-1)a}{K}\right)A.
\end{aligned}
\]

这给出式 (1)。当 \(\eta=1\) 时式 (6) 已给出 \(B\le A\)，无需除以 \(\eta-1\)。

## 3. 可直接核对的非负 slack 证书

记 \(\gamma=1-1/\eta\)，定义

\[
E=\gamma Z+A/\eta-B,\quad
H=A+D-Z,\quad
J=\eta aR-KD,\quad
T=A-R.
\]

上面的四条论证分别给出 \(E,H,J,T\ge0\)，而且

\[
\boxed{
\left(1+\frac{(\eta-1)a}{K}\right)A-B
=E+\gamma H+\frac\gamma KJ+\frac{\gamma\eta a}{K}T.}
\tag{7}
\]

式 (7) 对符号 \(A,B,Z,D,R,a,K,\eta\) 是恒等式，已用 SymPy 独立核对。

第一项本身有三项非负分解：

\[
E=
\frac{o(Z-B)-Y}{o}
+\frac{Y-X}{o}
+\frac{uX-(Z-A)}{uo}.
\tag{8}
\]

单次交换也有完全展开。令

\[
p=\tilde d_s(S\setminus\{s\}),\quad
q=\tilde d_b(S\setminus\{s\}),\quad
g=d_b(S\setminus\{s\}).
\]

则

\[
uo\,r_s-D_b
=u(or_s-p)+u(p-q)+(uq-g)+(g-D_b),\tag{9}
\]

四项分别对应上误差带、预测交换最优性、下误差带、真实目标的 submodularity。式 (8)、(9) 同样已符号核对。

这也准确指出 H-E 原先失败的位置：无需给 \(f(S\cap O)\) 找正下界；约束传递通过 \(S\cup O\) 与所有交换完成。

## 4. 与之匹配的对手构造

先考虑 \(n>K\)。固定任意确定性算法，向它提供

\[
\tilde f(T)=b|T|,\qquad b>0.
\]

其完整查询 transcript 和输出都确定。若输出少于 \(K\) 个元素，任意补成一个 \(K\)-集合 \(S\)。令真实目标为 modular，权重为

\[
w_e=\begin{cases}
b/o,&e\in S,\\
ub,&e\notin S.
\end{cases}
\]

写 \(a_0=\min\{K,n-K\}\)。一个最优解取 \(a_0\) 个高权元素与 \(K-a_0\) 个低权元素，因此

\[
\frac{f(S)}{f(O)}
=\frac{Kb/o}{a_0ub+(K-a_0)b/o}
=\frac{K}{K+(\eta-1)a_0}.
\]

原算法若输出更小的集合，其真实价值不超过 \(f(S)\)。因此上界覆盖所有输出大小至多为 \(K\) 的确定性算法。

每个非零集合增加量是若干权重之和，所以单元素或 all-pairs 定义下均满足该误差带。单独取高权元素和低权元素分别达到 \(u\) 与 \(o\)，故实际误差因子恰好是指定拆分。

当 \(n=K\) 时，输出整个 ground set 达到比值 1。若还要求实际误差两端恰好取到，不能使用“全部低权”的退化构造；在至少两个元素上分别设置高、低权即可，最优输出仍为整个 ground set。

J5 对 24 个有理参数 modular 实例精确检查了 37,056 个非空 all-pairs 增加量，包括 \(n=K\) 的校准端点，全部通过。

## 5. 范围与不能随之升级的结论

- 算法保证使用 \(|S|=K\)，这是穷举算法本身的定义。上界通过补足输出覆盖 \(|S|<K\) 的算法。
- 不需要“重叠最小”的假设；最小重叠仅用于从逐实例式 (1) 取最坏值。
- 需要 \(\tilde f(S)\ge\tilde f(O)\) 与全部交换比较。只有 one-swap local optimality 时，不能直接调用这个证明。
- 穷举可能查询 \(\binom nK\) 个集合；这里没有得到多项式查询算法，也没有改变有限预算 hardness 的适用范围。
- 随机算法需要单独分析。这个确定性值不能称为有限 \(n\) 的随机 minimax 值。

最后一点有直接反证：\(n=3,K=2,\eta=3\) 时确定性值为 \(1/2\)，但均匀随机输出一个二元集，对任何单调 submodular 目标都保证期望至少 \((2/3)f(N)\ge(2/3)\mathrm{OPT}\)。一般事实是均匀 \(K\)-子集的期望值至少 \((K/n)f(N)\)，可沿随机排列的非增期望边际求和得到。此随机论证为 `[HAND-PROOF-UNREVIEWED]`，不在本次符号 oracle 的断言范围内。

## 6. 论文如何使用

正文可把原 ceiling 定理改成一个统一的确定性陈述，单列现有随机上界。附录加入本证明的三步消元及式 (7)，并明确全局带在并集处的作用。

这个新增点的理论价值来自证明机制：对手即使只公开线性预测，也能达到最坏值；而对任意合法预测函数，算法侧的保证由全部交换与同一个并集上的误差耦合锁定。它不是对交集价值作一个未经支持的均匀分配假设。
