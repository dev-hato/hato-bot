import type { Context } from "@actions/github/lib/context";
import type { GitHub } from "@actions/github/lib/utils";
import type {RestEndpointMethodTypes} from "@octokit/plugin-rest-endpoint-methods";

export async function script(
  github: InstanceType<typeof GitHub>,
  context: Context,
): Promise<number> {
  const pullsListParams: RestEndpointMethodTypes["pulls"]["list"]["parameters"] = {
    owner: context.repo.owner,
    repo: context.repo.repo,
    head: context.repo.owner + ":develop",
    base: "master",
    state: "open",
  };
  console.log("call pulls.list:", pullsListParams);
  const pulls = await github.paginate(github.rest.pulls.list, pullsListParams);
  return pulls.length;
}
