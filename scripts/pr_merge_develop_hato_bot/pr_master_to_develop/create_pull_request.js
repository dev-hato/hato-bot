const script = require(`${process.env.GITHUB_WORKSPACE}/scripts/create_pull_request.js`)

module.exports = async ({github, context}) => {
    const common_params = {
        owner: context.repo.owner,
        repo: context.repo.repo
    }
    const pulls_create_params = {
        head: process.env.ORG_NAME + ":master",
        base: "develop",
        title: "master -> develop",
        body: "鳩の歴史は同期される\ndevelopに新たなコミットがpushされる前にマージしてね！",
        ...common_params
    }
    script({github, pulls_create_params, common_params})
}
