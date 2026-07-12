# `thumb` Pipeline — Complete Command Reference

> **Shell syntax differs.** Every command block shows both.  
> MINGW64/Git Bash → use the `bash` block.  
> PowerShell → use the `powershell` block.

---

## Step 0 — Environment Setup
> Run this at the start of every new terminal session.

### Activate the virtual environment

**Bash (MINGW64/Git Bash):**
```bash
source .venv/Scripts/activate
```

**PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

> After activation your prompt shows `(.venv)`. Confirm it worked:

**Bash:**
```bash
pip list
# Should show google-genai, rembg, Pillow and other project packages
```

**PowerShell:**
```powershell
pip list
# Should show google-genai, rembg, Pillow and other project packages
```

---

### Set real Gemini providers (session-scoped)

**Bash:**
```bash
export THUMB_PROVIDERS="gemini"
echo $THUMB_PROVIDERS      # confirm → prints: gemini
```

**PowerShell:**
```powershell
$env:THUMB_PROVIDERS = "gemini"
echo $env:THUMB_PROVIDERS  # confirm → prints: gemini
```

> Omit this step to stay on fake providers (safe default, no credits spent).  
> To revert mid-session:

**Bash:**
```bash
export THUMB_PROVIDERS="fake"
```

**PowerShell:**
```powershell
$env:THUMB_PROVIDERS = "fake"
```

---

## Step 1 — Onboard a Creator
> Run once per creator. Analyzes photos, runs the capture checklist, generates cutouts.

**Bash:**
```bash
thumb onboard srikar \
  --niche tech-explainer \
  --face on \
  --brand-color "#D82C2C" \
  --photos assets/faces/
```

**PowerShell:**
```powershell
thumb onboard srikar `
  --niche tech-explainer `
  --face on `
  --brand-color "#D82C2C" `
  --photos assets/faces/
```

### Check the onboarding report immediately — before anything else

**Bash:**
```bash
cat creators/srikar/asset-pack/onboarding-report.md
```

**PowerShell:**
```powershell
Get-Content creators\srikar\asset-pack\onboarding-report.md
```

> You need `accepted N photo(s)` with N > 0.  
> If `accepted 0` — the report tells you exactly why. Fix photos and re-onboard. **Do not proceed until photos are accepted.**

### Confirm cutouts were generated

**Bash:**
```bash
ls creators/srikar/asset-pack/cutouts/
```

**PowerShell:**
```powershell
dir creators\srikar\asset-pack\cutouts\
```

> Should show one `.png` per accepted photo.

### Re-onboard (after reshooting photos)
> Delete old photos AND their cached `.json` files first, then re-run onboard.

**Bash:**
```bash
rm -rf creators/srikar/asset-pack/photos/
mkdir creators/srikar/asset-pack/photos/
rm -rf creators/srikar/asset-pack/cutouts/
# Now copy new photos into assets/faces/ and re-run onboard
thumb onboard srikar --niche tech-explainer --face on --brand-color "#D82C2C" --photos assets/faces/
```

**PowerShell:**
```powershell
Remove-Item -Recurse -Force creators\srikar\asset-pack\photos\
New-Item -ItemType Directory creators\srikar\asset-pack\photos\
Remove-Item -Recurse -Force creators\srikar\asset-pack\cutouts\
# Now copy new photos into assets/faces/ and re-run onboard
thumb onboard srikar --niche tech-explainer --face on --brand-color "#D82C2C" --photos assets/faces/
```

---

## Step 2 — Build the Style Library
> Add reference thumbnails you admire. Run anytime — before or between orders.

### Add one reference

**Bash:**
```bash
thumb style add assets/inspirations/loop-engineering-is-dead.png \
  --niche tech-explainer
```

**PowerShell:**
```powershell
thumb style add assets\inspirations\loop-engineering-is-dead.png `
  --niche tech-explainer
```

### Add a reference scoped to a specific creator's Asset Pack

**Bash:**
```bash
thumb style add assets/inspirations/my-ref.png \
  --niche tech-explainer \
  --creator srikar
```

**PowerShell:**
```powershell
thumb style add assets\inspirations\my-ref.png `
  --niche tech-explainer `
  --creator srikar
```

### List all specs for a niche

**Bash:**
```bash
thumb style list --niche tech-explainer
```

**PowerShell:**
```powershell
thumb style list --niche tech-explainer
```

> You want 3–5 specs with genuinely different `text_device` and `backdrop` values — not just different accent colors. If everything clusters into chips/red, add more varied references.

---

## Step 3 — Start an Order

**Bash:**
```bash
thumb order new srikar \
  --title "All You Need To Know About Harness Engineering" \
  --hook "Harness Engineering Explained"
```

**PowerShell:**
```powershell
thumb order new srikar `
  --title "All You Need To Know About Harness Engineering" `
  --hook "Harness Engineering Explained"
```

> Prints an Order ID, e.g. `created order 001 for srikar`. Note it — every command below uses it.

### Confirm the order was created

**Bash:**
```bash
cat creators/srikar/orders/001/brief.md
# Should show your title, hook, and Status: new
```

**PowerShell:**
```powershell
Get-Content creators\srikar\orders\001\brief.md
# Should show your title, hook, and Status: new
```

---

## Step 4 — Run the Pipeline
> **Always run `--n 3` first. Never jump straight to 20.**

### Trial run — 3 candidates (~₹9)

**Bash:**
```bash
thumb order run srikar 001 --n 3
```

**PowerShell:**
```powershell
thumb order run srikar 001 --n 3
```

### Open the Contact Sheet

**Bash:**
```bash
thumb order sheet srikar 001
# Opens in your browser automatically
```

**PowerShell:**
```powershell
thumb order sheet srikar 001
# Opens in your browser automatically
```

### Check a candidate's metadata (confirm face is present)

**Bash:**
```bash
cat creators/srikar/orders/001/cand-01/metadata.json
# Look for: source_photo (NOT null), placement decisions, style_spec used
# If you see source_photo: null or "source-photo limitation" → STOP, do not scale
```

**PowerShell:**
```powershell
Get-Content creators\srikar\orders\001\cand-01\metadata.json
# Look for: source_photo (NOT null), placement decisions, style_spec used
# If you see source_photo: null or "source-photo limitation" → STOP, do not scale
```

### Check the cost ledger after the trial run

**Bash:**
```bash
python -c "
import json
total = sum(json.loads(l)['cost_usd'] for l in open('creators/srikar/orders/001/ledger.jsonl'))
print(f'USD {total:.4f}  (~Rs.{total*86:.0f})')
"
# Should be ~$0.10 / ₹9 for 3 candidates
```

**PowerShell:**
```powershell
python -c "
import json
total = sum(json.loads(l)['cost_usd'] for l in open('creators/srikar/orders/001/ledger.jsonl'))
print(f'USD {total:.4f}  (~Rs.{total*86:.0f})')
"
# Should be ~$0.10 / ₹9 for 3 candidates
```

---

### Decision gate after the trial 3

```
Faces present in Contact Sheet?
Text legible and inside margins?
Backgrounds varied (not all the same)?

YES to all → scale to 20
NO to any  → STOP. Read metadata. Run /diagnosing-bugs before spending more.
```

---

### Scale to full 20 candidates (~₹68 total including the trial 3)

**Bash:**
```bash
thumb order run srikar 001 --n 20
thumb order sheet srikar 001
```

**PowerShell:**
```powershell
thumb order run srikar 001 --n 20
thumb order sheet srikar 001
```

> Note: re-running regenerates all 20 — the trial 3 are re-spent. Total ≈ 23 images ≈ ₹68.

### Verify final cost

**Bash:**
```bash
python -c "
import json
total = sum(json.loads(l)['cost_usd'] for l in open('creators/srikar/orders/001/ledger.jsonl'))
print(f'USD {total:.4f}  (~Rs.{total*86:.0f})')
"
# Should land near $0.75–0.80 / ₹65–70
```

**PowerShell:**
```powershell
python -c "
import json
total = sum(json.loads(l)['cost_usd'] for l in open('creators/srikar/orders/001/ledger.jsonl'))
print(f'USD {total:.4f}  (~Rs.{total*86:.0f})')
"
# Should land near $0.75–0.80 / ₹65–70
```

---

## Step 5 — Curate
> Mark 2–3 candidates for delivery after judging the Contact Sheet.

**Bash:**
```bash
thumb order curate srikar 001 --picks cand-03,cand-07,cand-12
```

**PowerShell:**
```powershell
thumb order curate srikar 001 --picks cand-03,cand-07,cand-12
```

### Confirm status updated

**Bash:**
```bash
cat creators/srikar/orders/001/brief.md
# Status should now show: curated
```

**PowerShell:**
```powershell
Get-Content creators\srikar\orders\001\brief.md
# Status should now show: curated
```

---

## Step 6 — Deliver

**Bash:**
```bash
thumb order deliver srikar 001
```

**PowerShell:**
```powershell
thumb order deliver srikar 001
```

### Confirm deliverables exist

**Bash:**
```bash
ls creators/srikar/orders/001/deliverables/
# Should show 2–3 clean 1280x720 PNGs ready to send to the creator
```

**PowerShell:**
```powershell
dir creators\srikar\orders\001\deliverables\
# Should show 2–3 clean 1280x720 PNGs ready to send to the creator
```

---

## Step 7 — Revise
> Re-renders ONLY the affected layer. Everything else is reused. Costs paise, not a full re-roll.

### New wording (re-renders Text layer only)

**Bash:**
```bash
thumb order revise srikar 001 \
  --candidate cand-07 \
  --change "wording: Make Loops Simple"
```

**PowerShell:**
```powershell
thumb order revise srikar 001 `
  --candidate cand-07 `
  --change "wording: Make Loops Simple"
```

### Different photo (re-renders Subject layer only)

**Bash:**
```bash
thumb order revise srikar 001 \
  --candidate cand-07 \
  --change "photo: face02.png"
```

**PowerShell:**
```powershell
thumb order revise srikar 001 `
  --candidate cand-07 `
  --change "photo: face02.png"
```

### New direction (re-renders Background layer only)

**Bash:**
```bash
thumb order revise srikar 001 \
  --candidate cand-07 \
  --change "direction: brighter, more hopeful tone"
```

**PowerShell:**
```powershell
thumb order revise srikar 001 `
  --candidate cand-07 `
  --change "direction: brighter, more hopeful tone"
```

### Check the revision in the Contact Sheet

**Bash:**
```bash
thumb order sheet srikar 001
```

**PowerShell:**
```powershell
thumb order sheet srikar 001
```

> Confirm only that candidate changed — other candidates' files should be byte-identical.

---

## Step 8 — Close the Order

**Bash:**
```bash
thumb order deliver srikar 001
# Re-export including any revised picks
```

**PowerShell:**
```powershell
thumb order deliver srikar 001
# Re-export including any revised picks
```

---

## Utility Commands

### List all orders and their status

**Bash:**
```bash
thumb order list srikar         # orders for one creator
thumb order list                # all orders across all creators
```

**PowerShell:**
```powershell
thumb order list srikar
thumb order list
```

### Read the onboarding report anytime

**Bash:**
```bash
cat creators/srikar/asset-pack/onboarding-report.md
```

**PowerShell:**
```powershell
Get-Content creators\srikar\asset-pack\onboarding-report.md
```

### Run the entire pipeline on fakes (zero credits, for testing)

**Bash:**
```bash
export THUMB_PROVIDERS="fake"
thumb order run srikar 001 --n 3
thumb order sheet srikar 001
```

**PowerShell:**
```powershell
$env:THUMB_PROVIDERS = "fake"
thumb order run srikar 001 --n 3
thumb order sheet srikar 001
```

---

## Budget Safety Rules

```
1. ALWAYS run --n 3 first. Judge the Contact Sheet. Only then scale to --n 20.

2. ALWAYS read the onboarding report before order run.
   Zero accepted photos = order run will refuse loudly (by design).

3. ALWAYS check candidate metadata after the trial 3.
   source_photo: null means the face bug is back. STOP before scaling.

4. ALWAYS check the ledger after the trial 3.
   If cost is already way over ₹9, something is wrong. STOP.

5. NEVER set THUMB_PROVIDERS=gemini in a test or debugging session.
   Use fakes for all dev work. Real providers only for real orders.
```

---

## Shell Quick Reference

| What you want to do | Bash (MINGW64) | PowerShell |
|---|---|---|
| Set env variable | `export VAR="value"` | `$env:VAR = "value"` |
| Read env variable | `echo $VAR` | `echo $env:VAR` |
| Activate venv | `source .venv/Scripts/activate` | `.venv\Scripts\Activate.ps1` |
| Line continuation | `\` (backslash) | `` ` `` (backtick) |
| Read a file | `cat path/to/file` | `Get-Content path\to\file` |
| List folder | `ls path/` | `dir path\` |
| Delete folder | `rm -rf path/` | `Remove-Item -Recurse -Force path\` |
| Make folder | `mkdir path/` | `New-Item -ItemType Directory path\` |
