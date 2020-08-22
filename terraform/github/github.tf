resource "github_branch_protection" "develop" {
  branch = "develop"
  enforce_admins = true
  repository = "hato-bot"

  required_pull_request_reviews {
    dismiss_stale_reviews = true
    dismissal_teams = []
    dismissal_users = []
    require_code_owner_reviews = false
    required_approving_review_count = 1
  }

  required_status_checks {
    contexts = [
      "pr-format (3.8)",
      "pr-lint (3.8)",
      "pr-super-lint (3.8)",
      "pr-test (3.7)",
      "pr-test (3.8)",
      "pr-type-hint (3.7)",
      "pr-type-hint (3.8)",
      "runner / hadolint",
    ]
    strict = true
  }
}

resource "github_branch_protection" "master" {
  branch = "master"
  enforce_admins = true
  repository = "hato-bot"

  required_pull_request_reviews {
    dismiss_stale_reviews = true
    dismissal_teams = []
    dismissal_users = []
    require_code_owner_reviews = true
    required_approving_review_count = 1
  }

  required_status_checks {
    contexts = [
      "pr-docker",
      "pr-format (3.8)",
      "pr-lint (3.8)",
      "pr-super-lint (3.8)",
      "pr-test (3.7)",
      "pr-test (3.8)",
      "pr-type-hint (3.7)",
      "pr-type-hint (3.8)",
      "runner / hadolint",
    ]
    strict = true
  }
}
