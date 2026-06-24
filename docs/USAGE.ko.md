# cubrid-dev2-pr 사용 가이드 (팀원용)

CUBRID dev2 팀원들이 올린 **열려 있는 PR 목록**과 승인 현황, 그리고 **내 리뷰 상태**를
한눈에 보여주는 CLI/TUI 도구입니다. 데이터는 모두 `gh`(GitHub CLI)를 통해 가져옵니다.

## 1. 사전 준비물

- **Python 3.11 이상**
- **`gh` (GitHub CLI)** — 로그인되어 있어야 합니다.
  ```bash
  gh auth status      # 로그인 안 되어 있으면 아래 실행
  gh auth login
  ```
- **`uv`** — Python 도구 매니저 (https://docs.astral.sh/uv/)

> 인증·토큰은 이 도구가 따로 관리하지 않고 `gh` 설정을 그대로 사용합니다.

## 2. 설치

```bash
git clone https://github.com/vimkim/cubrid-dev2-pr.git
cd cubrid-dev2-pr

just install        # 권장 (내부적으로 uv tool install . 실행)
# 또는: uv tool install .
```

설치되면 `cubrid-dev2-pr` 명령이 `~/.local/bin`에 생깁니다. 확인:

```bash
cubrid-dev2-pr --version
```

- `~/.local/bin`이 `PATH`에 없으면 셸 설정(`.bashrc` / `.zshrc`)에 추가하세요.
- 코드 업데이트 후 재설치: `just reinstall` (또는 `uv tool install --force .`)

## 3. 최초 실행 & 설정 변경 (필수)

처음 실행하면 설정 파일이 **자동 생성**됩니다.

```
~/.config/cubrid-dev2-pr/config.toml
```

기본값은 `reviewer = "vimkim"` 입니다. **반드시 본인 GitHub 아이디로 바꿔야**
"내 리뷰(MY REVIEW)" 컬럼이 본인 기준으로 올바르게 표시됩니다.

`~/.config/cubrid-dev2-pr/config.toml` 을 열어 수정하세요:

```toml
# cubrid-dev2-pr configuration
# 추적할 팀원들의 GitHub 로그인 목록
teammates = [
  "hgryoo", "hornetmj", "hyahong", "vimkim", "H2SU",
  "YeunjunLee", "youngjun9072", "InChiJun", "lht1199",
]

# "내 리뷰" 기준 사용자 → 본인 GitHub 아이디로 변경! (vimkim 아님)
reviewer = "my-github-id"

repo  = "CUBRID/cubrid"   # 대상 저장소
limit = 300               # 가져올 PR 최대 개수
```

> 예) 본인 아이디가 `hyahong` 이면 `reviewer = "hyahong"`.
> 설정 파일을 고치기 싫으면 실행할 때마다 `--reviewer` 로 덮어쓸 수도 있습니다(아래 참고).

## 4. 사용법

```bash
cubrid-dev2-pr                      # 기본: 팀원들의 열린 PR을 색상 표로 출력 (draft 숨김)
cubrid-dev2-pr --drafts            # draft PR도 포함
cubrid-dev2-pr --reviewer hyahong  # 설정 안 고치고 내 리뷰 기준만 일시 변경
cubrid-dev2-pr --repo CUBRID/cubrid
cubrid-dev2-pr --limit 50          # 가져올 개수 제한
cubrid-dev2-pr --tui               # 대화형 TUI 실행
```

표 컬럼: PR 번호 · 작성자 · 생성일 · 승인 현황(예: `3/9`) · 내 리뷰 상태 · 제목 · URL

**색상 의미**
- 초록 `APPROVED` / 빨강 `CHANGES_REQUESTED` / 노랑·흐림 `commented only`·`not reviewed` / 청록 `self-authored`
- 승인 비율: `0/N` 빨강, 일부 승인 노랑, 전원 승인 초록

**TUI 조작법**
- `↑` / `↓` : 행 이동
- `Enter` : 선택한 PR 상세 (작성자·승인 현황·리뷰어별 상태·PR 본문)
- `Esc` : 목록으로 복귀
- `q` 또는 `Ctrl-C` : 종료

## 5. 자주 묻는 질문

- **표가 비어 있어요** → 열린(open) PR이 없거나 draft만 있는 경우입니다. `--drafts` 를 붙여 보세요.
- **인증 오류** → `gh auth status` 로 GitHub CLI 로그인 상태부터 확인하세요.
- **MY REVIEW가 이상해요** → `config.toml` 의 `reviewer` 가 본인 아이디인지 확인하세요.

> 참고: 이 도구는 개발 진행 중이라 일부 기능(목록/표, 승인 통계, TUI)은 순차적으로 완성됩니다.
> 설치·설정 흐름은 위와 동일합니다.
