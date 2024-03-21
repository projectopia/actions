from typing import Dict, Optional

from pydantic import BaseModel, Field, constr

from projectopia.utils.github.constants import *


class RepositoryConfig(BaseModel):
    name: str = "projectopia"
    description: Optional[str] = None
    homepage: str = ""
    private: bool = False
    is_template: bool = False
    auto_init: bool = True


class APIConfig(BaseModel):
    token: str
    version: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")


class BranchProtectionRulesConfig(BaseModel):
    required_status_checks: Dict | None
    enforce_admins: bool | None
    required_pull_request_reviews: Dict | None
    restrictions: Dict | None
    required_linear_history: bool = False
    allow_force_pushes: bool = False
    allow_deletions: bool = False
    block_creations: bool = False
    required_conversation_resolution: bool = False
    lock_branch: bool = False
    allow_fork_syncing: bool = False


class GithubPagesConfig(BaseModel):
    source: Dict
    cname: str = None
