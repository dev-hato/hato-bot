module.exports = async ({github, pulls_create_params, common_params}) => {
    console.log("call pulls.create:", pulls_create_params)
    const create_pull_res = await github.rest.pulls.create(
        pulls_create_params
    )
    const number = create_pull_res.data.number
    const release_users = ["nakkaa"]
    const pulls_request_reviews_params = {
        pull_number: number,
        reviewers: release_users,
        ...common_params
    }
    console.log("call pulls.requestReviewers:")
    console.log(pulls_request_reviews_params)
    await github.rest.pulls.requestReviewers(
        pulls_request_reviews_params
    )
    const issues_add_assignees_params = {
        issue_number: number,
        assignees: release_users,
        ...common_params
    }
    console.log("call issues.addAssignees:")
    console.log(issues_add_assignees_params)
    await github.rest.issues.addAssignees(issues_add_assignees_params)
}
