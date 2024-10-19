import type {Context} from "@actions/github/lib/context";
import type { GitHub } from "@actions/github/lib/utils";
import type { RestEndpointMethodTypes } from "@octokit/plugin-rest-endpoint-methods";

export async function createPullRequestHatoBot(
  github: InstanceType<typeof GitHub>,
  context: Context,
  pullsCreateParams: RestEndpointMethodTypes["pulls"]["create"]["parameters"],
) {
  console.log("call pulls.create:", pullsCreateParams);
  const createPullRes = await github.rest.pulls.create(pullsCreateParams);
  const number = createPullRes.data.number;
  const releaseUsers = ["nakkaa"];
  const pullsRequestReviewsParams: RestEndpointMethodTypes["pulls"]["requestReviewers"]["parameters"] =
    {
      owner: context.repo.owner,
      repo: context.repo.repo,
      pull_number: number,
      reviewers: releaseUsers,
    };
  console.log("call pulls.requestReviewers:");
  console.log(pullsRequestReviewsParams);
  await github.rest.pulls.requestReviewers(pullsRequestReviewsParams);
  const issuesAddAssigneesParams: RestEndpointMethodTypes["issues"]["addAssignees"]["parameters"] =
    {
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: number,
      assignees: releaseUsers,
    };
  console.log("call issues.addAssignees:");
  console.log(issuesAddAssigneesParams);
  await github.rest.issues.addAssignees(issuesAddAssigneesParams);
}
