# Path: trigger/repo/__main__.py

import argparse
import os

from projectopia.utils.github.repository import PersonalRepository as GitHub


def main():
    parser = argparse.ArgumentParser(description="GitHub Repository Operations")
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Repository name",
    )
    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="GitHub token",
    )
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Branch name",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="docs",
        help="Source directory",
    )
    parser.add_argument(
        "--protection",
        type=bool,
        default=False,
        help="Enable branch protection",
    )
    parser.add_argument(
        "--pages",
        type=str,
        default="False",
        help="Enable GitHub Pages",
    )
    parser.add_argument(
        "--description",
        type=str,
        default="A GitHub repository",
        help="Repository description",
    )
    parser.add_argument(
        "--private",
        type=str,
        default="public",
        help="Repository visibility",
    )
    args = parser.parse_args()

    repo = GitHub(
        token=args.token,
        name=args.name,
        description=args.description,
        private=True if args.private.lower() == "private" else False,
        is_template=False,
        auto_init=True,
    )

    # Create the repository
    repo.create()

    if args.pages.lower() == "true":
        repo.add_branch(branch_name="gh-pages")
        repo.configure_github_pages(source="/", branch="gh-pages")
        repo.update_homepage()

    with open(os.getenv("GITHUB_ENV"), "a") as f:
        f.write(f"github-username={str(repo._get_username())}")


if __name__ == "__main__":
    main()
