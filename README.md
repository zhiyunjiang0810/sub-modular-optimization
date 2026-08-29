# 启动方式

1. 把这个目录放进一个新仓库，`git init && git add -A && git commit -m "init"`。
2. 在 tmux 里启动 Claude Code（`tmux new -s night`），工作目录为本目录。
   权限/自动批准的设置按官方文档配置（https://docs.claude.com/en/docs/claude-code/overview），
   本目录不需要写任何仓库外的路径。
3. 首条消息（复制下面整段）：

---
请先完整阅读 CLAUDE.md、RESEARCH_STATE.md、TASKS.md，然后按 TASKS.md 顺序执行 T1 到 T7。
严格遵守 CLAUDE.md 的状态标签规则：没有 oracle 确认的断言不准写 proved。
每个任务完成后 commit 并更新 REPORT.md；卡住 45 分钟就记录并跳到下一个。
全部完成后在 REPORT.md 顶部写 5 行以内的 summary，然后停止。不要向我提问，遇到需要决定的地方自己选保守的一种并记录理由。
---

4. 早上先看 `REPORT.md` 顶部，再看 `git log`，最后看 `results/`。
