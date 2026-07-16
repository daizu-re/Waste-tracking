import base64
import json
import os
import sys
import urllib.request
import urllib.error

OWNER = "daizu-re"
REPO = "Waste-tracking"


def get_env_token():
    return os.environ.get("GITHUB_TOKEN")


def read_token():
    token = get_env_token()
    if token:
        return token.strip()
    if sys.stdin.isatty():
        token = input("GitHub personal access token (repo scope): ").strip()
        return token
    raise RuntimeError(
        "GitHub token not found in GITHUB_TOKEN environment variable and interactive input unavailable."
    )


def github_api_request(url, method="GET", data=None, token=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "WasteTrackerUploader/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed: {exc.code} {exc.reason}\nURL: {url}\nResponse: {body}"
        )


def get_repo_info(token):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    return github_api_request(url, token=token)


def get_file_sha(path, token, branch):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={branch}"
    try:
        response = github_api_request(url, token=token)
        return response.get("sha")
    except RuntimeError as exc:
        if "404" in str(exc):
            return None
        raise


def upload_file(path, local_path, token, branch, commit_message):
    with open(local_path, "rb") as f:
        content_bytes = f.read()
    encoded = base64.b64encode(content_bytes).decode("ascii")
    sha = get_file_sha(path, token, branch)
    payload = {
        "message": commit_message,
        "content": encoded,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    result = github_api_request(url, method="PUT", data=payload, token=token)
    return result


def gather_files(root):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for filename in filenames:
            if filename == os.path.basename(__file__):
                continue
            local_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(local_path, root).replace(os.sep, "/")
            all_files.append((rel_path, local_path))
    return sorted(all_files)


def main():
    token = read_token()
    repo_info = get_repo_info(token)
    branch = repo_info.get("default_branch", "main")
    root = os.path.dirname(os.path.abspath(__file__))
    files = gather_files(root)
    if not files:
        print("No files found to upload.")
        return

    commit_message = "Upload Waste Collection Track project"
    print(f"Uploading {len(files)} files to {OWNER}/{REPO}@{branch}...")

    for rel_path, local_path in files:
        print(f"Uploading {rel_path}...")
        upload_file(rel_path, local_path, token, branch, commit_message)

    print("Upload complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
