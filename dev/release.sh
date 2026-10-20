#!/usr/bin/env bash
# 수강생용 브랜치 study를 main의 course/와 설치 파일로 갱신하고, 고객사에 보낼 zip을 만든다.
#
# 브랜치: dev(작업) → main(완성본, 병합) → study(수강생용, 이 스크립트가 만든다)
# 실행(프로젝트 루트, main에서): git switch main && git merge dev && bash dev/release.sh <버전>   예: v4
# - study는 개발 이력과 섞이지 않는 별도 브랜치(orphan)다. dev/·materials·인수인계 자료가 이력에도 남지 않는다.
# - 교안은 dev에서 고친다. study에서 직접 고치지 않는다.
# - push하지 않는다. 끝나면 dev로 돌아와 `git push origin study dev`로 원격을 맞춘다(원격 study가 수강생 기본 브랜치, 2026-10-17).
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
BRANCH=study
VERSION=${1:-v1}
REV=$(git rev-parse --short HEAD)
SRC_BRANCH=$(git rev-parse --abbrev-ref HEAD)
OUT_DIR="$HOME/800_Archives/830_Courses/samsung_ds_ai_developer"
ZIP="$OUT_DIR/$(date +%F)_course_${VERSION}.zip"
FILES=(course pyproject.toml uv.lock .python-version .env.sample .gitignore .agents)
# 수업 뒤에 공개할 것(2026-10-20 사용자 결정: 캡스톤 정답). study에서 뺀다. 공개할 때 비우고
# dev/builders/build_capstone_guide.py의 SHOW_ANSWERS를 True로 바꿔 다시 빌드한다
HIDDEN=(course/Chapter02/code/solution/06-capstone)

fail() { echo "✖ $1 | $2 | $3" >&2; exit 1; }

# 1. main에서, 보낼 파일이 모두 커밋된 상태여야 한다(작업 중인 변경이 섞이지 않게)
if [ "$SRC_BRANCH" != main ]; then
  fail "지금 브랜치가 $SRC_BRANCH" "study는 main에서만 만든다" "git switch main && git merge dev 후 다시 실행"
fi
if [ -n "$(git status --porcelain -- "${FILES[@]}")" ]; then
  fail "커밋 안 된 변경이 있음" "course/ 또는 설치 파일이 수정된 상태" "커밋한 뒤 다시 실행"
fi
echo "✔ [1/5] 보낼 파일이 모두 커밋됨 ($SRC_BRANCH@$REV)"

# 2. 커밋된 수강생본 검사: 저장된 출력·강사용 메모·키 파일이 없어야 한다
uv run python - "$REV" <<'PY' || fail "수강생본 검사 실패" "위 목록 참고" "빌더로 다시 만들고 출력을 지운 뒤 커밋"
import json, subprocess, sys
rev = sys.argv[1]
files = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, "course"], capture_output=True, text=True, check=True).stdout.split()
bad = [f for f in files if f.endswith(".env") or f.endswith("/app.py") and "/notebooks/" in f]
for f in files:
    if f.endswith(".ipynb"):
        nb = json.loads(subprocess.run(["git", "show", f"{rev}:{f}"], capture_output=True, text=True, check=True).stdout)
        for c in nb["cells"]:
            src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            if c.get("outputs") or c.get("execution_count"):
                bad.append(f"{f}: 저장된 출력")
                break
            if "<details><summary>강사용 메모</summary>" in src:
                bad.append(f"{f}: 강사용 메모")
                break
for b in bad:
    print("  -", b)
sys.exit(1 if bad else 0)
PY
echo "✔ [2/5] 수강생본 검사 통과(출력·강사용 메모·키 파일 없음)"

# 3. 임시 작업 폴더에서 수강생용 브랜치를 새 내용으로 맞춘다
WT=$(mktemp -d "${TMPDIR:-/tmp}/release_course.XXXXXX")
cleanup() { git worktree remove --force "$WT" >/dev/null 2>&1 || true; }
trap cleanup EXIT
git worktree add --detach -q "$WT"
if git show-ref --verify -q "refs/heads/$BRANCH"; then
  git -C "$WT" checkout -q "$BRANCH"
else
  git -C "$WT" checkout -q --orphan "$BRANCH"
fi
git -C "$WT" read-tree --empty  # 색인을 비우고
git -C "$WT" clean -fdq           # 작업 폴더의 파일도 비운다(새 내용으로 통째로 바꾸기 위해)
git archive "$REV" "${FILES[@]}" | tar -x -C "$WT"
for h in "${HIDDEN[@]}"; do rm -r "${WT:?}/$h"; done  # 임시 작업 폴더 안에서만 지운다(dev·main은 그대로)
# 맨 위로 복사한 안내의 폴더·문서 경로는 course/ 기준으로 바꾼다
sed -E -e 's#\| `(Chapter|config|agent_docs)#| `course/\1#g' -e 's#`agent_docs/#`course/agent_docs/#g' \
  "$WT/course/README.md" > "$WT/README.md"
sed -e 's#](agent_docs/#](course/agent_docs/#g' "$WT/course/AGENTS.md" > "$WT/AGENTS.md"
# .gitignore에서 강사·개발용 폴더(dev/, infra/, 보관 폴더) 줄은 뺀다
grep -v -E '^(/?dev/|infra/|/private/|/source_archives/)' "$WT/.gitignore" > "$WT/.gitignore.tmp" && mv "$WT/.gitignore.tmp" "$WT/.gitignore"
git -C "$WT" add -A
if git -C "$WT" diff --cached --quiet; then
  echo "✔ [3/5] 수강생용 브랜치 $BRANCH: 바뀐 내용 없음"
else
  git -C "$WT" commit -q -m "release: course from $SRC_BRANCH@$REV ($VERSION)"
  echo "✔ [3/5] 수강생용 브랜치 $BRANCH 갱신: $(git rev-parse --short "$BRANCH")"
fi

# 4. 수강생용 브랜치에 dev/가 없는지 확인
if git ls-tree -r --name-only "$BRANCH" | grep -q "^dev/"; then
  fail "수강생용 브랜치에 dev/가 있음" "복사 대상이 잘못됨" "FILES 목록 확인"
fi
for h in "${HIDDEN[@]}"; do
  if git ls-tree -r --name-only "$BRANCH" | grep -q "^$h/"; then
    fail "수강생용 브랜치에 $h가 있음" "수업 뒤 공개할 정답이 섞임" "HIDDEN 목록과 3번 단계 확인"
  fi
done
if git grep -q -I -E "(^|[^A-Za-z0-9./])dev/" "$BRANCH" -- . ':!uv.lock'; then
  git grep -n -I -E "(^|[^A-Za-z0-9./])dev/" "$BRANCH" -- . ':!uv.lock' >&2
  fail "수강생용 파일이 dev/를 가리킴" "위 줄" "dev에서 그 문구를 고친 뒤 다시 실행"
fi
echo "✔ [4/5] 수강생용 브랜치에 dev/ 폴더도, dev/를 가리키는 글도 없음"

# 5. zip 만들기(보관 폴더가 외장 드라이브라 연결되지 않았으면 임시 폴더에 만들고 알린다)
if ! mkdir -p "$OUT_DIR" 2>/dev/null; then
  echo "⚠ 보관 폴더 ${OUT_DIR}를 쓸 수 없음(외장 드라이브 연결 확인) → zip을 ~/000_Inbox/080_Temporary에 만든다. 나중에 보관 폴더로 옮긴다"
  OUT_DIR="$HOME/000_Inbox/080_Temporary"
  ZIP="$OUT_DIR/$(date +%F)_course_${VERSION}.zip"
  mkdir -p "$OUT_DIR"
fi
git archive "$BRANCH" --prefix=samsung_ds_ai_course/ -o "$ZIP"
echo "✔ [5/5] zip: $ZIP ($(du -h "$ZIP" | cut -f1))"
