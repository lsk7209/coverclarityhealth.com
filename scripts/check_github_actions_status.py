import argparse
import json
import subprocess
from datetime import datetime, timezone


def run(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None


def git_value(args):
    result = run(["git", *args])
    if result is None or result.returncode != 0:
        return ""
    return result.stdout.strip()


def gh_json(args):
    result = run(["gh", *args])
    if result is None:
        raise RuntimeError("GitHub CLI is not available")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh command failed")
    return json.loads(result.stdout or "[]")


def repo_name():
    result = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    if result is None:
        raise RuntimeError("GitHub CLI is not available")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh repo view failed")
    return result.stdout.strip()


def workflow_runs(repo, branch, workflow, limit=20):
    return gh_json([
        "run",
        "list",
        "--repo",
        repo,
        "--branch",
        branch,
        "--workflow",
        workflow,
        "--json",
        "databaseId,headSha,status,conclusion,workflowName,displayTitle,createdAt,event",
        "--limit",
        str(limit),
    ])


def run_for_head(runs, head):
    return next((item for item in runs if item.get("headSha") == head), None)


def run_summary(item):
    if not item:
        return None
    return {
        "databaseId": item.get("databaseId"),
        "workflowName": item.get("workflowName"),
        "displayTitle": item.get("displayTitle"),
        "status": item.get("status"),
        "conclusion": item.get("conclusion"),
        "createdAt": item.get("createdAt"),
        "event": item.get("event"),
        "headSha": item.get("headSha"),
    }


def check_workflow(repo, branch, head, workflow, required=True):
    runs = workflow_runs(repo, branch, workflow)
    current = run_for_head(runs, head)
    latest = runs[0] if runs else None
    ok = bool(current and current.get("status") == "completed" and current.get("conclusion") == "success")
    if not required and current is None:
        ok = True
    return {
        "name": workflow,
        "ok": ok,
        "required": required,
        "current_head_run": run_summary(current),
        "latest_run": run_summary(latest),
    }


def parse_github_time(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def check_latest_workflow(repo, branch, workflow, required=True, max_age_hours=None):
    runs = workflow_runs(repo, branch, workflow)
    latest = runs[0] if runs else None
    ok = bool(latest and latest.get("status") == "completed" and latest.get("conclusion") == "success")
    if not required and latest is None:
        ok = True
    age_hours = None
    if latest and latest.get("createdAt"):
        created_at = parse_github_time(latest.get("createdAt"))
        if created_at:
            age_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
    if ok and max_age_hours is not None and age_hours is not None and age_hours > max_age_hours:
        ok = False
    return {
        "name": workflow,
        "ok": ok,
        "required": required,
        "current_head_run": None,
        "latest_run": run_summary(latest),
        "scope": "latest",
        "latest_age_hours": round(age_hours, 2) if age_hours is not None else None,
        "max_age_hours": max_age_hours,
    }


def main():
    parser = argparse.ArgumentParser(description="Check GitHub Actions status for the current launch commit.")
    parser.add_argument("--require-gsc-success", action="store_true", help="Require the GSC sitemap workflow to have succeeded for the current HEAD.")
    parser.add_argument("--skip-scheduled-check", action="store_true", help="Do not check the latest scheduled publishing workflow result.")
    parser.add_argument("--scheduled-max-age-hours", type=float, default=2.0, help="Maximum accepted age for the latest scheduled publishing run.")
    args = parser.parse_args()

    head = git_value(["rev-parse", "--verify", "HEAD"])
    branch = git_value(["branch", "--show-current"]) or "main"
    repo = repo_name()
    checks = [
        check_workflow(repo, branch, head, "Content quality", required=True),
        check_workflow(repo, branch, head, "Submit sitemap to Google Search Console", required=args.require_gsc_success),
    ]
    if not args.skip_scheduled_check:
        checks.append(check_latest_workflow(
            repo,
            branch,
            "Publish scheduled content",
            required=True,
            max_age_hours=args.scheduled_max_age_hours,
        ))
    report = {
        "passed": all(item["ok"] for item in checks),
        "repo": repo,
        "branch": branch,
        "head": head,
        "checks": checks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
