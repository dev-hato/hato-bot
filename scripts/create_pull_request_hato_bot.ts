import type { GitHub } from "@actions/github/lib/utils";
import type { RestEndpointMethodTypes } from "@octokit/plugin-rest-endpoint-methods";

export async function createPullRequestHatoBot(
  github: InstanceType<typeof GitHub>,
  pullsCreateParams: RestEndpointMethodTypes["pulls"]["create"]["parameters"],
  commonParams: {
    owner: string;
    repo: string;
  },
) {
  console.log("call pulls.create:", pullsCreateParams);
  const createPullRes = await github.rest.pulls.create(pullsCreateParams);
  const number = createPullRes.data.number;
  const releaseUsers = ["nakkaa"];
  const pullsRequestReviewsParams: RestEndpointMethodTypes["pulls"]["requestReviewers"]["parameters"] =
    {
      pull_number: number,
      reviewers: releaseUsers,
      ...commonParams,
    };
  console.log("call pulls.requestReviewers:");
  console.log(pullsRequestReviewsParams);
  await github.rest.pulls.requestReviewers(pullsRequestReviewsParams);
  const issuesAddAssigneesParams: RestEndpointMethodTypes["issues"]["addAssignees"]["parameters"] =
    {
      issue_number: number,
      assignees: releaseUsers,
      ...commonParams,
    };
  console.log("call issues.addAssignees:");
  console.log(issuesAddAssigneesParams);
  await github.rest.issues.addAssignees(issuesAddAssigneesParams);
}
