const script = require(
  `${process.env.GITHUB_WORKSPACE}/scripts/create_pull_request_hato_bot.js`,
);

module.exports = async ({ github, context }) => {
  const commonParams = {
    owner: context.repo.owner,
    repo: context.repo.repo,
  };
  const pullsCreateParams = {
    head: context.repo.owner + ":master",
    base: "develop",
    title: "master -> develop",
    body: "鳩の歴史は同期される\ndevelopに新たなコミットがpushされる前にマージしてね！",
    ...commonParams,
  };
  script({ github, pullsCreateParams, commonParams });
};
