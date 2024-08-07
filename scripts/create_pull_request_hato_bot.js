module.exports = async ({ github, pullsCreateParams, commonParams }) => {
  console.log("call pulls.create:", pullsCreateParams);
  const createPullRes = await github.rest.pulls.create(pullsCreateParams);
  const number = createPullRes.data.number;
  const releaseUsers = ["nakkaa"];
  const pullsRequestReviewsParams = {
    pull_number: number,
    reviewers: releaseUsers,
    ...commonParams,
  };
  console.log("call pulls.requestReviewers:");
  console.log(pullsRequestReviewsParams);
  await github.rest.pulls.requestReviewers(pullsRequestReviewsParams);
  const issuesAddAssigneesParams = {
    issue_number: number,
    assignees: releaseUsers,
    ...commonParams,
  };
  console.log("call issues.addAssignees:");
  console.log(issuesAddAssigneesParams);
  await github.rest.issues.addAssignees(issuesAddAssigneesParams);
};
