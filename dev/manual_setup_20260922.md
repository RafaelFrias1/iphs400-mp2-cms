## Repo B — `iphs400-mp2-cms-starter` (public)

**B1. Confirm it's public and the tree is the student subset.**

```bash
cd ~/code/iphs400-mp2-cms-starter
gh repo view --json isPrivate      # {"isPrivate":false}
ls -la                             # app/ templates/ scripts/ tests/ docs/ notes/ .claude/ CLAUDE.md README.md
ls docs                            # exactly 3 files: student manual, rubric, hook guide
```

**B2. Prove nothing instructor-only came across.**

```bash
ls | grep -E 'solutions|grading|template$' && echo "WRONG TREE — you copied the dev repo" || echo "clean"
grep -rl "INSTRUCTOR-ONLY" . || echo "no instructor blocks"
```

If the wrong tree landed here: `git rm -r --cached . && rm -rf *` and re-copy from the student archive, or just let `publish_student_repo.py --apply` write it.

**B3. Commit and push.**

```bash
git add -A
git commit -m "MP2 starter: T00 skeleton, hooks, exercises, docs"
git push -u origin main
```

**B4. Turn on template mode and Issues.** This is the step that has no equivalent in the dev repo, and forgetting it is the most likely launch-day failure.

```bash
gh repo edit --template --enable-issues
```

**B5. Create the four labels** that `/to-tickets` will use, which template copies inherit.

```bash
for L in "spec:5319E7:The project spec" "ticket:0E8A16:A tracer-bullet ticket" \
         "stretch:FBCA04:Extra-credit goal" "bug:D73A4A:Defect found during review"; do
  IFS=: read -r n c d <<< "$L"; gh label create "$n" --color "$c" --description "$d" --force
done
gh label list
```

**B6. Look at it as a student would.**

```bash
gh repo view --web
```
Confirm: a green **Use this template** button, an Issues tab, `docs/` with three files, and no `solutions/` or instructor manuals.

**B7. From now on, never edit this repo directly.** Edit in the dev repo and publish. A direct edit here is silently overwritten by the next `--apply`.

## After both — shared steps

**S1. Pin the base SHA** (the judge can't run the authorship check without it). The SHA comes from the *student* repo; the edit happens in the *dev* repo.

```bash
cd ~/code/iphs400-mp2-cms-starter-dev
SHA=$(git -C ~/code/iphs400-mp2-cms-starter rev-parse HEAD)
sed -i '' "s|template_base_commit: .*|template_base_commit: $SHA|" rubric/mp2-grading-rubric_*.md
grep template_base_commit rubric/mp2-grading-rubric_*.md
git add -A && git commit -m "Rubric: pin template base commit" && git push
python3 scripts/publish_student_repo.py --apply --message "Rubric update"
```
(Linux or WSL2: drop the `''` after `-i`.)

**S2. Walk the student path once, then throw it away.**

```bash
cd ~/code
gh repo create iphs400-mp2-cms-selftest --template jon-chun/iphs400-mp2-cms-starter --public --clone
cd iphs400-mp2-cms-selftest && uv sync && cp .env.example .env && uv run cms serve
```
Open `http://localhost:8000/admin` → *T00: hello admin*. Then `Ctrl+C` and:

```bash
cd .. && gh repo delete jon-chun/iphs400-mp2-cms-selftest --yes && rm -rf iphs400-mp2-cms-selftest
```

If S2 works, you can launch. Students need only the repo URL.