#!/usr/bin/env bash
# 전달 브랜치 release/course를 지금 커밋의 course/와 설치 파일로 갱신하고, 고객사에 보낼 zip을 만든다.
#
# 실행(프로젝트 루트): bash scripts/release.sh [버전]      예: bash scripts/release.sh v1
# - 전달 브랜치는 개발 이력과 섞이지 않는 별도 브랜치(orphan)다. dev/·materials·인수인계 자료가 이력에도 남지 않는다.
# - 교안은 개발 브랜치에서 고치고 이 스크립트로 전달 브랜치를 갱신한다. 전달 브랜치에서 직접 고치지 않는다.
# - push하지 않는다.
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
BRANCH=release/course
VERSION=${1:-v1}
REV=$(git rev-parse --short HEAD)
SRC_BRANCH=$(git rev-parse --abbrev-ref HEAD)
OUT_DIR="$HOME/800_Archives/830_Courses/samsung_ds_ai_developer"
ZIP="$OUT_DIR/$(date +%F)_course_${VERSION}.zip"
FILES=(course pyproject.toml uv.lock .env.sample .gitignore)

fail() { echo "✖ $1 | $2 | $3" >&2; exit 1; }

# 1. 보낼 파일이 모두 커밋되어 있어야 한다(작업 중인 변경이 섞이지 않게)
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

# 3. 임시 작업 폴더에서 전달 브랜치를 새 내용으로 맞춘다
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
cp "$WT/course/README.md" "$WT/README.md"
cp "$WT/course/AGENTS.md" "$WT/AGENTS.md"
git -C "$WT" add -A
if git -C "$WT" diff --cached --quiet; then
  echo "✔ [3/5] 전달 브랜치 $BRANCH: 바뀐 내용 없음"
else
  git -C "$WT" commit -q -m "release: course from $SRC_BRANCH@$REV ($VERSION)"
  echo "✔ [3/5] 전달 브랜치 $BRANCH 갱신: $(git rev-parse --short "$BRANCH")"
fi

# 4. 전달 브랜치에 dev/가 없는지 확인
if git ls-tree -r --name-only "$BRANCH" | grep -q "^dev/"; then
  fail "전달 브랜치에 dev/가 있음" "복사 대상이 잘못됨" "FILES 목록 확인"
fi
echo "✔ [4/5] 전달 브랜치에 dev/ 없음"

# 5. zip 만들기
mkdir -p "$OUT_DIR"
git archive "$BRANCH" --prefix=samsung_ds_ai_course/ -o "$ZIP"
echo "✔ [5/5] zip: $ZIP ($(du -h "$ZIP" | cut -f1))"
