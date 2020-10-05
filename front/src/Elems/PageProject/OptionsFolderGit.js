import React, { useContext, useEffect, useState } from "react"
import AppContext from "../../context/application/appContext"
import Loader from "../AppComponents/Loader"
import { displayStringDate } from "../componentUtils"

const OptionsFolderGit = ({ folderID, prjID, repoStatus }) => {
  // Get repo information from server
  const { repository, repoGet, repoAccess } = useContext(AppContext)
  const [inToken, setInToken] = useState("")
  // // Util
  // const circleRepoGet = (save_id, folder_id) => {
  //   if (!repository || repository.folder_id !== folder_id){
  //     repoGet(save_id, folder_id)
  //   window.setTimeout(()=>{
  //     console.log('One more circle',repository, Boolean(repository))
  //     if (!repository || repository.folder_id !== folder_id) circleRepoGet(save_id, folder_id)
  //   }, 3000)}
  // }

  useEffect(() => {
    // circleRepoGet(prjID, folderID)
    if (!repository || repository.folder !== folderID) {
      console.log("CHECK THIS", prjID, folderID, repository)
      console.log("CHECK THIS", repository.folder !== folderID)
      repoGet(prjID, folderID)
    }
    console.log("REPO STATUS", repoStatus ? "true" : "false")
    // eslint-disable-next-line
  }, [repository, folderID, prjID])

  if (!repository.hasOwnProperty("name")) return <Loader />

  if (repository.error)
    return (
      <div>
        <h1>Ошибка репозитория: {repository.error}</h1>
      </div>
    )

  const saveTokenByEnter = (e) => {
    if (e.key === "Enter") saveToken(e)
  }
  const saveToken = (e) => {
    if (inToken.trim()) repoAccess(prjID, folderID, "token", inToken.trim())
  }

  const redirectToProvider = () => {
    // let [consumerKey, response_type, providerAuthUrl, scope] = [null] * 4
    let [consumerKey, response_type, providerAuthUrl, scope] = [null, null, null, null] // FIXME: [null] * 4
    switch (repository.provider) {
      case "bitbucket.org":
        consumerKey = "xckDCgTDkpEAtWnfYe"
        response_type = "code"
        providerAuthUrl = "https://bitbucket.org/site/oauth2/authorize"
        break
      case "github.com":
        consumerKey = "55aa8a87265bfa0f5ccf"
        providerAuthUrl = "https://github.com/login/oauth/authorize"
        scope = "repo"
        break
      case "gitlab.com":
        consumerKey = ""
        providerAuthUrl = "https://gitlab.com/oauth/authorize"
        break
      default:
        return
    }
    localStorage.setItem("oauth_callback_folder", folderID)
    localStorage.setItem("oauth_callback_save_id", prjID)

    let redirectTo = `${providerAuthUrl}?client_id=${consumerKey}`
    redirectTo += response_type ? `&response_type=${response_type}` : ""
    redirectTo += scope ? `&scope=${scope}` : ""
    window.location = redirectTo
  }

  return (
    <div>
      <div>
        <h1>Информация о репозитории (обновлена {displayStringDate(repository.updated)})</h1>
        <div>Провайдер: {repository.provider}</div>
        <div>Владелец: {repository.owner}</div>
        <div>Название: {repository.name}</div>
        {Boolean(repository.path) && <div>Путь: {repository.path}</div>}
        <div>Hash: {repository.sha}</div>
      </div>
      <div>
        <h1>Доступ к репозиторию</h1>
        {repoStatus ? (
          <div>предоставлен</div>
        ) : (
          <>
            <div>Введите токен вашего репозитория или войдите с помощью</div>
            <button className='btn' onClick={redirectToProvider}>
              {repository.provider}
            </button>
            <div>Token</div>
            <input
              type='text'
              value={inToken}
              onChange={(e) => setInToken(e.target.value)}
              onKeyPress={saveTokenByEnter}
              onBlur={saveToken}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default OptionsFolderGit
