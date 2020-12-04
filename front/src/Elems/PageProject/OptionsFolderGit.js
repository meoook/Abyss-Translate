import React, { useContext, useEffect, useState } from 'react'
import AppContext from '../../context/application/appContext'
import Loader from '../AppComponents/Loader'
import { displayStringDate } from '../componentUtils'

const OptionsFolderGit = ({ folderID, prjID, repoStatus }) => {
  // Get repo information from server
  const { repository, repoCheck, repoGet, repoAccess } = useContext(AppContext)
  const [inToken, setInToken] = useState('')
  const [gitState, setGitState] = useState(0)

  useEffect(() => {
    switch (repoStatus) {
      case true:
        setGitState(1) // 1 - success
        break
      case false:
        setGitState(-1) // -1 = fail
        break
      default:
        setGitState(0) // 0 = loading
        break
    }
  }, [repoStatus])

  useEffect(() => {
    let timer = window.setTimeout(() => {
      repoCheck(prjID, folderID).then((success) => {
        console.log("ONE MORE TIMER CIRCLE", success)
        if (success) repoGet(prjID, folderID)
        // if (!success) timer()
        // else repoGet(prjID, folderID)
      })
    }, 3000)
    return () => {
      window.clearTimeout(timer)
    }
    // eslint-disable-next-line
  }, [gitState])

  const saveTokenByEnter = (e) => {
    if (e.key === 'Enter') saveToken(e)
  }
  const saveToken = (e) => {
    if (inToken.trim()) repoAccess(prjID, folderID, 'token', inToken.trim())
  }

  const redirectToProvider = () => {
    // FIXME: Move to Reducer
    // let [consumerKey, response_type, providerAuthUrl, scope] = [null] * 4
    let [consumerKey, response_type, providerAuthUrl, scope] = Array(4).fill(
      null
    )
    switch (repository.provider) {
      case 'bitbucket.org':
        consumerKey = 'xckDCgTDkpEAtWnfYe'
        response_type = 'code'
        providerAuthUrl = 'https://bitbucket.org/site/oauth2/authorize'
        break
      case 'github.com':
        consumerKey = '55aa8a87265bfa0f5ccf'
        providerAuthUrl = 'https://github.com/login/oauth/authorize'
        scope = 'repo'
        break
      case 'gitlab.com':
        consumerKey =
          '56fcf0ae30f04c6d0bfa1a327274eb81a2c3bf6d64f1b5927ac0d2f47ef4ecdf'
        providerAuthUrl = 'https://gitlab.com/oauth/authorize'
        break
      default:
        return
    }
    localStorage.setItem('oauth_callback_folder', folderID)
    localStorage.setItem('oauth_callback_save_id', prjID)

    let redirectTo = `${providerAuthUrl}?client_id=${consumerKey}`
    redirectTo += response_type ? `&response_type=${response_type}` : ''
    redirectTo += scope ? `&scope=${scope}` : ''
    window.location = redirectTo
  }

  if (!gitState) return <Loader />

  if (!repository.hasOwnProperty('name'))
    return (
      <div>
        <h1>Ошибка - репозиторий не определен</h1>
      </div>
    )

  return (
    <div>
      <div>
        <h1>
          Информация о репозитории (обновлена{' '}
          {displayStringDate(repository.updated)})
        </h1>
        <div>Провайдер: {repository.provider}</div>
        <div>Владелец: {repository.owner}</div>
        <div>Название: {repository.name}</div>
        {Boolean(repository.path) && <div>Путь: {repository.path}</div>}
        <div>Hash: {repository.sha}</div>
      </div>
      <div>
        <h1>Доступ к репозиторию</h1>
        {gitState > 0 ? (
          <div className="t-green">предоставлен</div>
        ) : (
          <div className="t-red">{repository.error}</div>
        )}
        <hr />
        <div>Введите токен вашего репозитория или войдите с помощью</div>
        <button className="btn" onClick={redirectToProvider}>
          {repository.provider}
        </button>
        <div>Token</div>
        <input
          type="text"
          value={inToken}
          onChange={(e) => setInToken(e.target.value)}
          onKeyPress={saveTokenByEnter}
          onBlur={saveToken}
        />
      </div>
    </div>
  )
}

export default OptionsFolderGit
