const script = require(`${process.env.GITHUB_WORKSPACE}/scripts/create_pull_request_hato_bot.js`);

module.exports = async ({ github, context }) => {
  const commonParams = {
    owner: context.repo.owner,
    repo: context.repo.repo,
  };
  const pullsCreateParams = {
    head: context.repo.owner + ":develop",
    base: "master",
    title: "リリース",
    body: "鳩は唐揚げになるため、片栗粉へ飛び込む",
    draft: true,
    ...commonParams,
  };
  script({ github, pullsCreateParams, commonParams });
};
