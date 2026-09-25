import type { Context } from "@actions/github/lib/context";
import type { GitHub } from "@actions/github/lib/utils";
import type { RestEndpointMethodTypes } from "@octokit/plugin-rest-endpoint-methods";

export async function script(
  github: InstanceType<typeof GitHub>,
  context: Context,
) {
  const actionsCreateWorkflowDispatchParams: RestEndpointMethodTypes["actions"]["createWorkflowDispatch"]["parameters"] =
    {
      owner: context.repo.owner,
      repo: "sudden-death",
      workflow_id: 2452313,
      ref: "master",
    };
  console.log("call actions.createWorkflowDispatch:");
  console.log(actionsCreateWorkflowDispatchParams);
  await github.rest.actions.createWorkflowDispatch(
    actionsCreateWorkflowDispatchParams,
  );
}
