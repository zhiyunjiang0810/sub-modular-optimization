"""V11 Q10: assemble results/V11/VERIFICATION_MATRIX.md from the workflow
outputs (results/V11/workflow_result.json, dumped by the main session from
the structured returns of the four agent roles) plus the on-disk reports.

Label rule (TASKS11):
  [VERIFIED-CROSS]        A, B, C, D, E all pass
  [HAND-PROOF-UNREVIEWED] B or E has a GAP (C and D pass)
  [FAILED]                C or D failed (any violated inequality)
  [VERIFIED-ORACLE-ONLY]  C (and D) pass but B is missing entirely
The main session may override a label with an explicit reason (column
"裁定理由"), e.g. when a route-two gap is a known hand-proof residue.

Run:  python3 results/V11/build_matrix.py
"""
import json
import os

V11 = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(V11, 'workflow_result.json')))
OVER = json.load(open(os.path.join(V11, 'matrix_overrides.json'))) if os.path.exists(os.path.join(V11, 'matrix_overrides.json')) else {}

META = {
    'nobound': ('prop:necessity (alias prop:nobound)', 'Prop 1', 'app:necessity + appendix_model_proofs.tex (unwired)'),
    'valueacc': ('prop:valueacc', 'Prop 2', 'appendix_model_proofs.tex (convention B) + app:valueacc (old)'),
    'ceiling': ('thm:ceiling', 'Proposition (upper bound for unbounded queries)', 'app:ceiling + J5_ceiling_proof.md; route yi: appendix_model_proofs remark'),
    'guarantee': ('prop:guarantee', 'Prop 3', 'app:guarantee'),
    'coherence': ('lem:coherence', 'Lemma', 'app:coherence + H_J3_gate_check.py'),
    'exact': ('thm:exact', 'Theorem 1', 'app:exact + app:validity'),
    'limit': ('cor:limit', 'Corollary', 'app:asymptotics'),
    'linear_exact': ('thm:linear-exact', 'Theorem 2', 'app:greedybudget + results/J6/linear_exact.md'),
    'hardness': ('thm:hardness', 'Theorem 3', 'app:hardness'),
    'linear_anysize': ('thm:linear-anysize', 'Proposition (J7)', 'app:hardness-anysize + results/J7/linear_anysize.md'),
    'probelottery': ('J8 ProbeLottery', 'Proposition (J8)', 'GAP: proof file undelivered; results/J8/J8_claude_spotcheck.py'),
}


def label_for(key, r):
    o = OVER.get(key, {})
    if 'label' in o:
        return o['label'], o.get('reason', '')
    orc, aud, cmp_, bl = r.get('oracle'), r.get('audit'), r.get('compare'), r.get('blind')
    C_fail = (orc is None) or bool(orc.get('failed')) or any(c['status'] == 'FAIL' for c in orc.get('C', []))
    D_fail = (orc is None) or orc.get('D_violations', 1) > 0
    if C_fail or D_fail:
        return '[FAILED]', 'C 或 D 有失败项（见 oracle 列）'
    B_missing = (bl is None) or (cmp_ is None) or cmp_.get('verdict') == 'B-MISSING'
    if B_missing:
        return '[VERIFIED-ORACLE-ONLY]', '路线二缺失或路线一缺失'
    B_gap = (not cmp_.get('consistent')) or (not cmp_.get('quantifier_match')) or bool(cmp_.get('route2_gaps')) or cmp_.get('verdict', '').startswith('B-GAP') or cmp_.get('verdict', '').startswith('B-FAIL')
    E_gap = (aud is None) or bool(aud.get('gaps')) or (not aud.get('A_match', False))
    if B_gap or E_gap:
        return '[HAND-PROOF-UNREVIEWED]', 'B 或 E 有 GAP（见对应列）'
    return '[VERIFIED-CROSS]', '五项全过'


def cell(s, n=400):
    s = str(s).replace('\n', ' ').replace('|', '/')
    return s if len(s) <= n else s[:n] + ' ...'


# statements.md is split at its "## " headers; each key maps to the header
# substrings whose sections hold the verbatim ledger and paper statements.
STMT_HEADERS = {
    'nobound': ['prop:nobound'], 'valueacc': ['T2 prop:valueacc', 'T2 方案二'],
    'ceiling': ['thm:ceiling'], 'guarantee': ['prop:guarantee'],
    'coherence': ['lem:coherence'], 'exact': ['thm:exact'], 'limit': ['cor:limit'],
    'linear_exact': ['thm:linear-exact'], 'hardness': ['thm:hardness'],
    'linear_anysize': ['thm:linear-anysize'], 'probelottery': ['J8 ProbeLottery'],
}


def verbatim_sections():
    text = open(os.path.join(V11, 'statements.md')).read().split('\n')
    secs, cur, buf = {}, None, []
    for line in text:
        if line.startswith('## '):
            if cur is not None:
                secs[cur] = '\n'.join(buf).strip()
            cur, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if cur is not None:
        secs[cur] = '\n'.join(buf).strip()
    out = {}
    for key, subs in STMT_HEADERS.items():
        parts = []
        for h, body in secs.items():
            if any(s in h for s in subs):
                parts.append(f'#### {h}\n\n' + body.replace('\n### ', '\n##### '))
        out[key] = '\n\n'.join(parts) if parts else '(statements.md 无对应节)'
    return out


def main():
    rows = []
    for r in R['results']:
        key = r['key']
        label, why = label_for(key, r)
        orc, aud, cmp_, bl = r.get('oracle') or {}, r.get('audit') or {}, r.get('compare') or {}, r.get('blind') or {}
        lab, num, route1 = META[key]
        Cs = '; '.join(f"{c['name']}: {c['status']}" for c in orc.get('C', [])) or 'n/a'
        Dd = f"random {orc.get('D_random_count', 'n/a')}, structured {len(orc.get('D_structured', []))}, violations {orc.get('D_violations', 'n/a')}, worst {cell(orc.get('D_worst', ''), 120)}"
        Bv = f"{cmp_.get('verdict', 'n/a')}; consistent={cmp_.get('consistent')}, quantifiers={cmp_.get('quantifier_match')}; divergences: {cell('; '.join(cmp_.get('divergences', [])), 300) or 'none'}; route-2 gaps: {cell('; '.join(cmp_.get('route2_gaps', [])), 300) or 'none'}"
        Ev = ('全对应' if aud.get('A_match') and not aud.get('gaps') else f"A_match={aud.get('A_match')}; A_diffs: {cell('; '.join(aud.get('A_diffs', [])), 250) or 'none'}; GAP: {cell('; '.join(aud.get('gaps', [])), 300) or 'none'}")
        precise = OVER.get(key, {}).get('precise_statement', '(见 statements.md 的正文陈述；量词审计无 GAP 时可原样抄)')
        walk = orc.get('running_example', '') or OVER.get(key, {}).get('walk', '')
        rows.append((lab, num, route1, Bv, Cs, Dd, Ev, label, why, precise, walk, key))
    out = ['# VERIFICATION_MATRIX (V11, 2026-09-18)\n',
           '标准：A 陈述逐字（台账 vs 正文量词比对）；B 两条独立推导（路线一仓库证明，路线二盲审 Opus 子代理，只给 Definition 1 方案二、模型假设、陈述、记号表）；',
           'C oracle（sympy 恒等式、有理格点精确不等式、穷举合法性、精确 LP/对偶）；D 陈述反例搜索（随机 ≥ 2000 + 结构化）；E 量词审计表。',
           '标签规则：五项全过 [VERIFIED-CROSS]；B 或 E 有 GAP [HAND-PROOF-UNREVIEWED]；C 或 D 失败 [FAILED]；C 过 B 缺 [VERIFIED-ORACLE-ONLY]。',
           '每行细节：results/V11/route2/<key>.md（路线二）、oracle/<key>.{py,log,json,md}（C/D）、audit/<key>.md（A/E）、compare/<key>.md（B 比对）。\n']
    out.append('| label | 正文编号 | 陈述原文 | 路线一位置 | 路线二结论一致? (B) | oracle 项目与结果 (C) | 反例搜索 (D) | 量词审计 (E) | 最终标签 | 裁定理由 | 可写进正文的精确表述 | K=3, η=3/2 数字走读 |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for (lab, num, route1, Bv, Cs, Dd, Ev, label, why, precise, walk, key) in rows:
        out.append(f"| {lab} | {num} | 逐字见下方明细 §{lab}（源 statements.md） | {cell(route1, 150)} | {cell(Bv, 500)} | {cell(Cs, 500)} | {cell(Dd, 300)} | {cell(Ev, 400)} | **{label}** | {cell(why, 200)} | {cell(precise, 600)} | {cell(walk, 300)} |")
    verb = verbatim_sections()
    out.append('\n## 逐条明细（主表各列的未截断版本；陈述原文逐字取自 statements.md）\n')
    for (lab, num, route1, Bv, Cs, Dd, Ev, label, why, precise, walk, key) in rows:
        out.append(f'### {lab} ({num}) — 最终标签 **{label}**\n')
        out.append('**陈述原文**\n')
        out.append(verb.get(key, ''))
        out.append('\n**路线一位置**: ' + route1)
        out.append('\n**B 路线二比对**: ' + str(Bv))
        out.append('\n**C oracle**: ' + str(Cs))
        out.append('\n**D 反例搜索**: ' + str(Dd))
        out.append('\n**E 量词审计**: ' + str(Ev))
        out.append('\n**裁定理由**: ' + str(why))
        out.append('\n**可写进正文的精确表述**: ' + str(precise))
        out.append('\n**K=3, η=3/2 走读**: ' + str(walk).replace('\n', ' '))
        out.append('')
    out.append('\n## 重点发现（供作者判断；不进正文）\n')
    for i, f in enumerate(OVER.get('_findings', []), 1):
        out.append(f'{i}. {f}')
    out.append('\n## 缺失与限制\n')
    out.append('- J8：证明文件 results/J8/probe_lottery.md 未送达，路线一为 GAP；(3)、(8)–(12) 的 LP 对偶证书无法给出。')
    out.append('- J9（Q11）：证明文件未送达；C1 内联不等式已过，盲审路线二 PARTIAL（results/V11/route2/j9.md），不入矩阵主表。')
    out.append('- 盲审子代理输入清单（TASKS11 要求记录）：results/V11/inputs/{definition1,assumptions,notation}.md + statement_<key>.md（linear_anysize 另给 anysize_template.md；j9 用 statement_j9.md）。子代理被禁止读取其他任何文件；每份 route2/<key>.md 末尾列出实际读过的文件。')
    out.append('- 标签口径：TASKS11 五项规则严格执行；"裁定理由"列说明 GAP 的性质（陈述措辞 vs 证明缺口）与一行修订后可达的标签。')
    open(os.path.join(V11, 'VERIFICATION_MATRIX.md'), 'w').write('\n'.join(out) + '\n')
    print('rows:', len(rows))
    for r in rows:
        print(f"  {r[0]:<28} {r[7]}")


if __name__ == '__main__':
    main()
