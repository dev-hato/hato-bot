const fs = require('fs')
const hatoBotPackage = require(`${process.env.GITHUB_WORKSPACE}/hato-bot/package.json`)
const hatoBotPackageLock = require(`${process.env.GITHUB_WORKSPACE}/hato-bot/package-lock.json`)
const suddenDeathPackage = require(`${process.env.GITHUB_WORKSPACE}/sudden-death/package.json`)
const suddenDeathPackageLock = require(`${process.env.GITHUB_WORKSPACE}/sudden-death/package-lock.json`)

module.exports = () => {
  delete hatoBotPackage.scripts

  for (const packageKey of Object.keys(hatoBotPackage)) {
    suddenDeathPackage[packageKey] = hatoBotPackage[packageKey]
  }

  fs.writeFileSync(`${process.env.GITHUB_WORKSPACE}/sudden-death/package.json`, JSON.stringify(suddenDeathPackage, null, '  ') + '\n', 'utf8')

  delete hatoBotPackageLock.name

  for (const packageLockKey of Object.keys(hatoBotPackageLock)) {
    suddenDeathPackageLock[packageLockKey] = hatoBotPackageLock[packageLockKey]
  }

  fs.writeFileSync(`${process.env.GITHUB_WORKSPACE}/sudden-death/package-lock.json`, JSON.stringify(suddenDeathPackageLock, null, '  ') + '\n', 'utf8')
}
