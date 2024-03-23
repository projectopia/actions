import json
import logging
from typing import Dict, List

import requests
from requests.exceptions import Timeout

from projectopia.utils.github.config import (
    APIConfig,
    BranchProtectionRulesConfig,
    GithubPagesConfig,
    RepositoryConfig,
)
from projectopia.utils.github.constants import DEFAULT_GITHUB_API_VERSION


class BaseRepository:
    def __init__(self, api_config: APIConfig, repo_config: RepositoryConfig):
        """Base class for creating a repository
        :param token: Personal access token
        :param config: Repository configuration
        :param version: GitHub API version
        """
        self._token = api_config.token
        self._version = api_config.version

        self._name = repo_config.name
        self._description = repo_config.description
        self._homepage = repo_config.homepage
        self._private = repo_config.private
        self._is_template = repo_config.is_template
        self._auto_init = repo_config.auto_init

        self._base_url = "https://api.github.com"
        self._headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": self._version,
        }

        # Logging
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Get username
        self._username = self._get_username()

    def _request(self, method: str, url: str, **kwargs):
        try:
            response = requests.request(
                method, url, headers=self._headers, timeout=10, **kwargs
            )
            return response
        except Timeout:
            self._logger.exception("Request timed out!")
            return None

    def _get_username(self):
        url = f"{self._base_url}/user"
        response = self._request("GET", url)
        if response.status_code == 200:
            return response.json()["login"]
        else:
            self._logger.exception(f"Failed to get username. Error: {response.text}")
            return None


class PersonalRepository(BaseRepository):
    def __init__(
        self,
        token: str,
        version: str = DEFAULT_GITHUB_API_VERSION,
        **data,
    ):
        api_config = APIConfig(token=token, version=version)
        repo_config = RepositoryConfig(**data)
        super().__init__(api_config=api_config, repo_config=repo_config)

    def create(self):
        payload = {
            "name": self._name,
            "description": self._description,
            "homepage": self._homepage,
            "private": self._private,
            "is_template": self._is_template,
            "auto_init": self._auto_init,
        }
        url = f"{self._base_url}/user/repos"
        response = self._request("POST", url, data=json.dumps(payload))
        if response.status_code == 201:
            self._logger.info("Repository created successfully!")
        else:
            self._logger.exception(
                f"Failed to create repository. Error: {response.text}"
            )
            return False
        return True

    def delete(self):
        url = f"{self._base_url}/repos/{self._username}/{self._name}"
        response = self._request("DELETE", url)
        if response.status_code == 204:
            self._logger.info("Repository deleted successfully!")
        else:
            self._logger.exception(
                f"Failed to delete repository. Error: {response.text}"
            )
            return False
        return True

    def add_collaborator(self, username: str):
        url = f"{self._base_url}/repos/{self._username}/{self._name}/collaborators/{username}"
        response = self._request("PUT", url)
        if response.status_code == 201:
            self._logger.info(f"Collaborator {username} added successfully!")
        else:
            self._logger.exception(
                f"Failed to add collaborator. Error: {response.text}"
            )
            return False
        return True

    def add_collaborators(self, usernames: List[str]):
        try:
            for username in usernames:
                self.add_collaborator(username)
        except Exception:
            self._logger.exception("Failed to add collaborators!")
            return False
        return True

    def add_branch(self, branch_name: str, from_branch: str = "main"):
        url = f"{self._base_url}/repos/{self._username}/{self._name}/git/refs"
        branches = self._request("GET", url).json()
        branch = list(
            filter(lambda x: x["ref"] == f"refs/heads/{from_branch}", branches)
        )
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": branch[0]["object"]["sha"],
        }
        response = self._request("POST", url, data=json.dumps(payload))
        if response.status_code == 201:
            self._logger.info(f"Branch {branch_name} added successfully!")
        else:
            self._logger.exception(f"Failed to add branch. Error: {response.text}")
            return False
        return True

    def add_branches(self, branch_components: Dict[str, str]):
        try:
            for branch_name, from_branch in branch_components.items():
                self.add_branch(branch_name, from_branch)
        except Exception:
            self._logger.exception("Failed to add branches!")
            return False
        return True

    def set_branch_protection_rules(self, branch_name: str, **kwargs):
        branch_protection_rules_config = BranchProtectionRulesConfig(**kwargs)
        url = f"{self._base_url}/repos/{self._username}/{self._name}/branches/{branch_name}/protection"
        payload = branch_protection_rules_config.model_dump()
        response = self._request("PUT", url, data=json.dumps(payload))
        if response.status_code == 200:
            self._logger.info(f"Branch protection rules set successfully!")
        else:
            self._logger.exception(
                f"Failed to set branch protection rules. Error: {response.text}"
            )
            return False
        return True

    def configure_github_pages(self, source: str, branch: str = "main", **kwargs):
        github_pages_config = GithubPagesConfig(
            source={"branch": branch, "path": source},
            **kwargs,
        )
        url = f"{self._base_url}/repos/{self._username}/{self._name}/pages"
        payload = github_pages_config.model_dump()
        response = self._request("POST", url, data=json.dumps(payload))
        if response.status_code == 201:
            self._logger.info(f"GitHub Pages configured successfully!")
        else:
            self._logger.exception(
                f"Failed to configure GitHub Pages. Error: {response.text}"
            )
            return False
        return True

    def update_github_pages(self, source: str, branch: str = "main", **kwargs):
        github_pages_config = GithubPagesConfig(
            source={"branch": branch, "path": source},
            **kwargs,
        )
        url = f"{self._base_url}/repos/{self._username}/{self._name}/pages"
        payload = github_pages_config.model_dump()
        response = self._request("PUT", url, data=json.dumps(payload))
        if response.status_code == 204:
            self._logger.info(f"GitHub Pages updated successfully!")
        else:
            self._logger.exception(
                f"Failed to update GitHub Pages. Error: {response.text}"
            )
            return False
        return True

    def delete_github_pages(self):
        url = f"{self._base_url}/repos/{self._username}/{self._name}/pages"
        response = self._request("DELETE", url)
        if response.status_code == 204:
            self._logger.info(f"GitHub Pages deleted successfully!")
        else:
            self._logger.exception(
                f"Failed to delete GitHub Pages. Error: {response.text}"
            )
            return False
        return True

    def update_homepage(self):
        # Use github api to add homepage to the repository
        # https://docs.github.com/en/rest/reference/repos#update-a-repository
        url = f"https://api.github.com/repos/{self._username}/{self._name}"
        headers = {
            "Authorization": f"token {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }
        if self._name == f"{self._username}.github.io":
            data = {
                "homepage": f"https://{self._username}.github.io",
            }
            response = requests.patch(url, headers=headers, json=data)
            if response.status_code == 200:
                self._logger.info("Homepage added successfully!")
            else:
                self._logger.error(f"Failed to add homepage. Error: {response.text}")
        else:
            data = {
                "homepage": f"https://{self._username}.github.io/{self._name}",
            }
            response = requests.patch(url, headers=headers, json=data)
            if response.status_code == 200:
                self._logger.info("Homepage added successfully!")
            else:
                self._logger.error(f"Failed to add homepage. Error: {response.text}")
