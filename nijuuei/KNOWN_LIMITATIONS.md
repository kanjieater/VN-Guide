# 二重影 — Known Evidence Limitations

This guide targets the original 2000 Windows PC release.

The repository owner has explicitly accepted the two evidence limitations below so that the guide can ship without further source hunting. Video/gameplay evidence is out of scope for resolving these items.

## 命 route

SagaoZ directly documents the retained completion path and its 命 ending.

The independent BIGLOBE walkthrough documents the overall affection/ending system, but does not independently verify the exact retained affinity path. In particular, BIGLOBE classifies several choices retained from SagaoZ as 楓玲-affinity choices and documents different 命-affinity checkpoints.

Legacy independent Japanese text walkthroughs were located in search indexes, but their source pages could not be directly inspected in the current research environment (timeout / HTTP 403). Under the repository standards, they therefore cannot be promoted to Set B.

Status: **known owner-accepted evidence limitation; not an accuracy PASS**.

## 楓玲 route

SagaoZ directly documents the split:

`セーブ5から → 何もいわない`

and the resulting 楓玲 path.

BIGLOBE independently documents the highest-affinity heroine ending framework, but it does not print the exact `何もいわない` branch text. Its annotation `※命ルートの場合のみ選択肢発生` is not treated as direct evidence for the opposite 楓玲 choice.

Legacy independent Japanese text walkthroughs were again located in search indexes, but their source pages could not be directly inspected.

Status: **known owner-accepted evidence limitation; not an accuracy PASS**.

## Resolved review finding

The 命 / 舞 BAD detour previously reused BIGLOBE's generic bad-ending prose as if it documented Set-A-only exact actions. That defect was corrected in commit `42ab310c677dde63cae4c1957a7d898e837d63d8`; those exact A-only detour steps now use the permitted Set-B omission marker.

## Review-state note

This file documents the owner's decision to accept incomplete independent evidence for these two facts. It does not alter or override the repository's normal verification standard, and it does not claim reviewer approval for 命 or 楓玲.
