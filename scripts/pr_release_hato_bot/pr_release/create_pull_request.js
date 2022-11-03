const script = require(`${process.env.GITHUB_WORKSPACE}/scripts/create_pull_request.js`)

module.exports = async ({github, context}) => {
    const common_params = {
        owner: context.repo.owner,
        repo: context.repo.repo
    }
    const pulls_create_params = {
        head: process.env.ORG_NAME + ":develop",
        base: "master",
        title: "リリース",
        body: "鳩は唐揚げになるため、片栗粉へ飛び込む",
        draft: true,
        ...common_params
    }
    script({github, pulls_create_params, common_params})
}
