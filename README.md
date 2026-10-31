# GARCON — Garmin Connect → ChatGPT 🏃

[🇸🇪 Läs på svenska](README.sv.md) · [Garmin Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api/) · [MIT License](LICENSE)

**Your Garmin workouts, ready for analysis in ChatGPT — without manually copying every workout.**

GARCON is a small, open-source Python tool that uses Garmin's **official Personal API** to export selected activity, sleep, and recovery summaries to a JSON file. It can run **automatically in your own PRIVATE GitHub repository** using GitHub Actions, or **entirely on your computer**. ChatGPT may then read the JSON through its GitHub connection (if available on your account), or you can upload the file manually.

**This is NOT an official Garmin or OpenAI product.** No central GARCON account, backend, or hosted database is involved. Each person uses their own Garmin API key and is responsible for their own data.

## 🚨 IMPORTANT: YOUR PRIVATE HEALTH DATA WILL BE STORED ON GITHUB

> **IF YOU ENABLE THE GITHUB ACTIONS SYNC, YOUR PERSONAL HEALTH AND FITNESS DATA IS SAVED TO GITHUB.**
>
> **WE STRONGLY RECOMMEND USING A PRIVATE REPOSITORY. NEVER USE A PUBLIC REPOSITORY FOR PERSONAL TRAINING DATA.**
>
> The exported file contains sensitive data such as **activity timestamps, workout types, distance, duration, heart rate, calories, and potentially sleep and HRV**. Activity titles may also reveal locations or personal details.
>
> **A private repository is NOT end-to-end encrypted private storage.** GitHub stores the data and its **commit history**, and people/apps you authorize may be able to access it. If you connect ChatGPT to the repo, you are additionally granting ChatGPT access to that repository content. Review the relevant services' privacy terms.
>
> **Safety guard:** The supplied GitHub Actions workflow checks the repository's current visibility through the GitHub API and **refuses to upload data if the repository is PUBLIC**. This is an extra protection, **not a substitute for choosing PRIVATE** and checking the actual visibility yourself.
>
> **Alternative:** Run GARCON locally instead. Your output stays on your computer unless you choose to upload or share it. See [Run locally](#run-locally-no-github-upload).

No real user data, Garmin API keys, tokens, or JSON exports are included in this template repository.

## What it does

- Retrieves selected **activities** from Garmin Connect, including durations, distances, heart rate, power and training load where available.
- Retrieves **sleep**, **HRV**, and daily summary values *if Garmin has recorded them and the API returns them*.
- Saves a minimized snapshot to **data/training.json**; does **not** export GPS tracks, raw activity files, account passwords, or Garmin API keys.
- On a new installation, attempts up to **90 days** of activity history. Subsequent syncs recheck the last **30 days**, retaining previously imported items for up to **365 days**.
- Fetches the previous **8 calendar days** of available health summaries.
- Uses Python **3.12+** and Garmin's official [Personal API Python client](https://github.com/garmin/connect-personal-api-python), version 1.0.0.
- Supports free-tier GitHub Actions within applicable usage limits. ChatGPT access is **separate** and may depend on your plan.

**Garmin Personal API is for personal use with your own Garmin data.** GARCON is a self-hosted personal tool, not a multi-user Garmin service. See [Garmin's FAQ](https://developer.garmin.com/gc-developer-program/personal/personal-faq).

## Quick setup — automatic sync in a PRIVATE GitHub repository

### 1. Make your own PRIVATE repository

1. Open [the GARCON source repository](https://github.com/13estfriend/garcon).
2. Click **Use this template → Create a new repository**.
3. Select **your own GitHub account** as owner and choose a name, such as **my-garmin-data**.
4. **Select PRIVATE**. Double-check the visibility before continuing.
5. Click **Create repository**.

**Important:** Do **not** just enable syncing on the original, public GARCON source repo. Do **not** use a public fork for real data. GitHub templates create a fresh repository without the source repo's commit history.

### 2. Create your personal Garmin API key

1. Log in to **[Garmin Connect](https://connect.garmin.com/)** in a browser.
2. Follow Garmin's official guide: [Create a Personal API Key](https://developer.garmin.com/gc-developer-program/personal/personal-api/).
3. Open Garmin's **Personal API Key** page, select **Create Key**, read and accept its terms, choose an expiration period, and select **Create**.
4. **Copy the key immediately**. Garmin shows it **only once**. Treat it like a password.

The key expires after the period you choose (Garmin offers up to one year). When it expires, create a new key and replace your GitHub secret.

### 3. Store the key securely as a GitHub Actions secret

You should now be in **YOUR PRIVATE repository**, not the public GARCON source.

1. Go to **Settings → Secrets and variables → Actions**.
2. Select **New repository secret**.
3. For **Name**, enter exactly:

   ~~~text
   GARMIN_PERSONAL_API_KEY
   ~~~

4. Paste **your entire Garmin API key** into **Secret**.
5. Select **Add secret**.

**Never** put your key in a code file, README, GitHub issue, commit, screenshot or ChatGPT message. GitHub secrets are provided to the workflow only when it runs.

### 4. Start the first synchronization

1. Open **Actions** in **your private repository**.
2. If GitHub asks you to enable Actions for this repository, review the workflows and enable them.
3. In the left sidebar, select **Sync Garmin training data**.
4. Select **Run workflow**, choose the default branch (usually **main**), then select **Run workflow**.
5. Open the run and verify that its steps finish successfully (green check).
6. Open **data/training.json** in your private repository. This file is created by the workflow only **after** its privacy check passes.

If the workflow stops with **GARCON SAFETY STOP**, your repo is public. Do not bypass the check: create a private repo.

If it reports **Missing GARMIN_PERSONAL_API_KEY**, recheck the secret's exact name and make sure it was created in your new private repository.

### 5. Done: automatic refresh

The default schedule is **06:25 and 20:25 in Europe/Stockholm** every day. Workflows are not guaranteed to start on the exact minute (GitHub may delay scheduled jobs). You can also run it manually whenever you like.

To view the file in your repository:

~~~text
https://github.com/YOUR-USERNAME/YOUR-PRIVATE-REPO/blob/main/data/training.json
~~~

Replace **YOUR-USERNAME** and **YOUR-PRIVATE-REPO** with your account and repository name. The link will only work for authorized viewers.

## Customize your sync frequency, times, and timezone

Open **YOUR PRIVATE repo → .github/workflows/sync.yml → Edit (pencil) → Commit changes**.

Near the top, find:

~~~yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '25 6,20 * * *'
      timezone: 'Europe/Stockholm'
~~~

**cron** has five fields: **minute hour day-of-month month day-of-week**. Times use the specified **IANA timezone**, so the Europe/Stockholm setting automatically follows local daylight-saving changes. If you remove the **timezone** line, GitHub defaults to **UTC**.

### Ready-made examples

Replace the schedule block with any one of these:

**Daily at 07:15 (Stockholm):**

~~~yaml
schedule:
  - cron: '15 7 * * *'
    timezone: 'Europe/Stockholm'
~~~

**Twice daily at 06:25 and 20:25 (Stockholm, default):**

~~~yaml
schedule:
  - cron: '25 6,20 * * *'
    timezone: 'Europe/Stockholm'
~~~

**Every 4 hours, on the hour (Stockholm):**

~~~yaml
schedule:
  - cron: '0 */4 * * *'
    timezone: 'Europe/Stockholm'
~~~

**Weekdays (Monday–Friday) at 18:10 (Stockholm):**

~~~yaml
schedule:
  - cron: '10 18 * * 1-5'
    timezone: 'Europe/Stockholm'
~~~

**Use another timezone:** Change the IANA name, e.g. **Europe/London**, **America/New_York**, or **Australia/Sydney**.

**Manual only:** Remove the **schedule:** block entirely, but retain **workflow_dispatch:**. Then run the workflow from the **Actions** page whenever you want.

**Practical advice:** Once or twice daily is more than enough for most people. Don't schedule excessive requests. GitHub has a minimum scheduling interval of five minutes, but that is not a recommendation to run so often. Frequent runs may encounter usage limits or Garmin rate limiting.

Official reference: [GitHub Actions schedule / cron syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Connect your PRIVATE GitHub repository to ChatGPT

> **This is an optional, separate step.** GARCON does not automatically connect Garmin to ChatGPT. The workflow writes a JSON file to GitHub; ChatGPT then **reads** that file **if the GitHub integration is available for your plan and ChatGPT experience**.
>
> **Important:** Not all ChatGPT plans or modes offer GitHub reading in normal chats. This is **not guaranteed to work on ChatGPT Free**, and available features can change. You can always use the manual file-upload alternative described below, subject to your plan's usage limits.

1. Open **ChatGPT → Settings → Plugins**.
2. Find **GitHub** and choose **Connect** (or the corresponding connection option shown in your account).
3. Follow GitHub's authorization process.
4. Under repository access, choose **Only select repositories** and select **your new PRIVATE GARCON repository**. Do not grant access to every repository unless necessary.
5. Approve and save the connection.
6. Return to ChatGPT. Newly connected repositories may take **about five minutes** to become available.
7. In a ChatGPT mode that offers GitHub access, ask it to read **data/training.json** from your repository.

Example prompt:

> Read data/training.json from my GitHub repository YOUR-USERNAME/YOUR-PRIVATE-REPO. Summarize my last seven days of training, identify endurance versus high-intensity work, and describe recovery trends when sleep and HRV data are available. State the latest sync time and flag missing data. Do not invent workouts.

If ChatGPT cannot see your private repo: check **Settings → Plugins → GitHub → repository access** (or [GitHub installed apps](https://github.com/settings/installations)) and verify the new repository is selected. GitHub organization policies may also require approval.

**Privacy:** This authorization grants ChatGPT access to repository content. It does not make your GitHub repository public. Only connect the repositories you intend to share with ChatGPT.

Official reference: [OpenAI — Connecting GitHub to ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt).

### If GitHub access isn't available in your ChatGPT plan

1. Open your **PRIVATE** GitHub repository and go to **data/training.json**.
2. Use the **Raw** / **Download** option while logged in.
3. Upload the JSON file directly to ChatGPT and ask for analysis.

This requires a manual upload after each refresh, but does **not** require granting ChatGPT persistent GitHub repository access. ChatGPT file uploads and analysis may have plan-specific limits.

## Run locally (no GitHub upload)

You can use GARCON **without GitHub Actions**. The JSON file stays on your computer unless **you** decide to copy, commit, upload, or share it.

### Requirements

- A Garmin Connect account and Personal API key
- Python **3.12 or later**
- Git (or download the GARCON code as a ZIP from GitHub)

### 1. Download the code

~~~bash
git clone https://github.com/13estfriend/garcon.git
cd garcon
~~~

Or select **Code → Download ZIP** on the GARCON repo page, unpack, and open a terminal in that folder.

### 2. Install Python dependencies

**macOS / Linux:**

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
~~~

**Windows PowerShell** (Python 3.12+ must be installed):

~~~powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

### 3. Run the exporter

**macOS / Linux** (with your virtual environment activated):

~~~bash
python scripts/sync_garmin.py
~~~

**Windows PowerShell:**

~~~powershell
.\.venv\Scripts\python.exe scripts/sync_garmin.py
~~~

If **GARMIN_PERSONAL_API_KEY** is not already defined, the script will **prompt for it without displaying the characters** when run in an interactive terminal. This avoids storing the key in command history. Do not share your terminal screen if it contains private data.

The result appears at:

~~~text
data/training.json
~~~

The template's **.gitignore** ignores JSON exports locally to help prevent accidental commits. **Never force-add the JSON file to a public repository.** The supplied GitHub Actions workflow uses force-add **only after confirming the destination repository is private**.

You can upload the JSON file directly to ChatGPT when needed. To run again, repeat the command. To fully automate local scheduling, use Windows Task Scheduler, cron, or your operating system's equivalent; make sure credentials are handled securely.

**Local data still needs protection:** Keep your computer secured and consider encrypted backups. Using local mode does not automatically delete files that you previously uploaded elsewhere.

## What exactly is saved?

**data/training.json** is a human- and AI-readable JSON snapshot with:

| Section | Examples |
|---|---|
| **activities** | Activity ID/type/title, start time, duration, distance, heart rate, power, calories, training load where available |
| **sleep** | Total, deep, light, REM and awake duration; sleep score if available |
| **hrv** | Night HRV and baseline/status when returned by Garmin |
| **daily** | Selected daily fields such as resting heart rate, steps, energy and stress when returned |
| **sync_status** | Number of values fetched and error counts |
| **last_sync_utc** | Time of last successful snapshot creation |

- **No GPS tracks or coordinate fields are intentionally exported.** That does **not** mean all sensitive information has been removed: names, sport types, times, heart rate, and other biometric values remain personal.
- Garmin sometimes labels exercises as **Other**; GARCON does not guess whether those are SkiErg, walking, or something else.
- Missing sleep or HRV isn't necessarily a failure: your watch may not have collected it yet or Garmin's endpoint may not return it.
- All values depend on what Garmin Connect actually contains and exposes.
- The JSON is **not** a medical record and its interpretation should not be treated as a diagnosis.

## Data retention and deletion

By default, GARCON retains entries for up to 365 days within the current JSON snapshot, but **past versions can remain in Git history**. Editing or deleting the file does **not** reliably erase old copies from GitHub's history.

To stop collection: disable or delete the scheduled workflow, remove your Garmin key secret, and optionally revoke the key in Garmin Connect. To remove your stored data, delete the file **and address repository history and any copies, forks, downloaded files, backups, and ChatGPT uploads**. For sensitive data, creating a completely new empty repository and deleting the old repository is often simpler than rewriting history; review GitHub's deletion and retention guidance.

If you accidentally committed health data to a **PUBLIC** repository, treat the data as potentially exposed. Make the repository private immediately, then address public history and any existing copies. Switching visibility later does not undo prior disclosure.

## Troubleshooting

| Problem | What to do |
|---|---|
| **SAFETY STOP: repository PUBLIC** | Create a new **PRIVATE** repo from the template. Do not disable the safety check |
| **Missing GARMIN_PERSONAL_API_KEY** | Add the secret in **your private repo**, using the exact name shown above |
| **401 / 403 or authorization error** | Check that the key is valid, not expired/revoked, and belongs to your own Garmin Connect account |
| **No training.json after running** | Open **Actions → Sync Garmin training data → latest run** and inspect the failed step |
| **Push rejected / contents permission** | Inspect **Settings → Actions → General** and organization policy; workflow requests **contents: write** |
| **Activities exist but no sleep/HRV** | Verify Garmin Connect has recorded them. Check **sync_status** and try after the device has synced |
| **ChatGPT cannot find your repo** | Verify the GitHub connection, repository access and available ChatGPT plan/mode; allow a few minutes |
| **Scheduled runs don't start** | Confirm Actions are enabled, workflow is on your default branch, and you haven't removed the schedule |

To test the code without a Garmin key:

~~~bash
python -m unittest discover -s tests -v
~~~

## Security, scope, costs and licensing

- **Always use PRIVATE GitHub repositories for health data.**
- **Do not commit secrets or JSON exports to a public Git history.**
- Each user is responsible for their own API key and third-party permissions.
- The tool can run without paid hosting. GitHub Actions free-tier limits and policies apply; ChatGPT app availability and pricing are independent.
- GARCON uses Garmin's official **Personal API** for **personal use**, not a commercial multi-user API integration.
- GARCON's code is available under the **MIT License**. Garmin's Python client is a separate dependency licensed under **Apache 2.0**.
- This project is independently developed and is **not affiliated with, sponsored by, or endorsed by Garmin or OpenAI**.

Happy training. 🚴
