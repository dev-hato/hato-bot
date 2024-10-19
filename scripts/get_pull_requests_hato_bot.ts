module.exports = async ({ github, context }) => {
  const pullsListParams = {
    owner: context.repo.owner,
    repo: context.repo.repo,
    head: context.repo.owner + ":develop",
    base: "master",
    state: "open",
  };
  console.log("call pulls.list:", pullsListParams);
  const pulls = await github.paginate(github.rest.pulls.list, pullsListParams);
  return pulls.length;
};
