#!/usr/bin/env python3
"""
Create Issue #9 in GitHub repository using GitHub REST API v3.

Usage:
    python create_issue_9.py --token <github_token>

Requirements:
    - GitHub Personal Access Token (classic) with 'repo' scope
    - Python 3.7+
    - requests library

Environment variable alternative:
    GITHUB_TOKEN=<token> python create_issue_9.py
"""

import os
import sys
import json
import requests
from pathlib import Path


def read_issue_content(content_file="ISSUE_9_CONTENT.md"):
    """Read issue content from markdown file."""
    file_path = Path(__file__).parent / content_file
    if not file_path.exists():
        print(f"Error: {content_file} not found at {file_path}")
        sys.exit(1)
    return file_path.read_text("utf-8")


def create_issue_on_github(owner, repo, token, title, body, labels=None):
    """
    Create issue on GitHub using REST API v3.
    
    Args:
        owner: GitHub username or org
        repo: Repository name
        token: GitHub Personal Access Token
        title: Issue title
        body: Issue body (markdown)
        labels: List of label names (optional)
    
    Returns:
        dict: API response with issue data
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Issue-Creator/1.0",
    }
    
    payload = {
        "title": title,
        "body": body,
    }
    
    if labels:
        payload["labels"] = labels
    
    print(f"Creating issue in {owner}/{repo}...")
    print(f"Title: {title}")
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        issue_data = response.json()
        issue_number = issue_data.get("number")
        issue_url = issue_data.get("html_url")
        
        print(f"\n✅ Issue created successfully!")
        print(f"   Issue #: {issue_number}")
        print(f"   URL: {issue_url}")
        
        return issue_data
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"❌ Authentication Failed (401)")
            print(f"   Check your GitHub token")
        elif e.response.status_code == 404:
            print(f"❌ Repository Not Found (404)")
            print(f"   Check owner/repo: {owner}/{repo}")
        elif e.response.status_code == 422:
            print(f"❌ Validation Failed (422)")
            print(f"   Response: {e.response.json()}")
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e.response.reason}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    # Get token from argument or environment
    token = None
    if len(sys.argv) > 2 and sys.argv[1] == "--token":
        token = sys.argv[2]
    else:
        token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("Error: GitHub token required")
        print()
        print("Usage:")
        print("  python create_issue_9.py --token <github_token>")
        print()
        print("Or set GITHUB_TOKEN environment variable:")
        print("  export GITHUB_TOKEN=<token>")
        print("  python create_issue_9.py")
        sys.exit(1)
    
    # Repository info
    owner = "valentinaasilva"
    repo = "fiware-smart-store"
    
    # Read issue content
    body = read_issue_content()
    
    # Extract title from first line
    lines = body.split("\n")
    title = lines[0].strip().lstrip("#").strip()
    
    # Create issue
    labels = ["feature", "data-model", "nice-to-have"]
    
    issue_data = create_issue_on_github(
        owner=owner,
        repo=repo,
        token=token,
        title=title,
        body=body,
        labels=labels
    )
    
    print("\nIssue content preview:")
    print("=" * 80)
    print(body[:500] + "...")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
