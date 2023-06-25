module.exports = async ({ github, context }) => {
  const reposCreateDispatchEventParams = {
    owner: context.repo.owner,
    repo: 'sudden-death',
    event_type: 'pr-copy-ci'
  }
  console.log('call repos.createDispatchEvent:')
  console.log(reposCreateDispatchEventParams)
  await github.rest.repos.createDispatchEvent({
    ...reposCreateDispatchEventParams
  })
}
