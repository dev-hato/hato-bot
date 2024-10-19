import type { Context } from "@actions/github/lib/context";
import type { GitHub } from "@actions/github/lib/utils";
import type { RestEndpointMethodTypes } from "@octokit/plugin-rest-endpoint-methods";
import { createPullRequestHatoBot } from "../../create_pull_request_hato_bot";

export async function script(
  github: InstanceType<typeof GitHub>,
  context: Context,
) {
  const commonParams = {
    owner: context.repo.owner,
    repo: context.repo.repo,
  };
  const pullsCreateParams: RestEndpointMethodTypes["pulls"]["create"]["parameters"] =
    {
      head: context.repo.owner + ":develop",
      base: "master",
      title: "リリース",
      body: "鳩は唐揚げになるため、片栗粉へ飛び込む",
      draft: true,
      ...commonParams,
    };
  await createPullRequestHatoBot(github, pullsCreateParams, commonParams);
}
