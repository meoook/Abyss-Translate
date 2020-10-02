import React, { useContext, useEffect, useState } from "react"
import AppContext from "../../context/application/appContext"
import Loader from "../AppComponents/Loader"
import { displayStringDate } from "../componentUtils"

const OptionsFolderGit = ({ folderID, prjID }) => {
  // Get repo information from server
  const { repository, repoGet, repoAccess } = useContext(AppContext)
  const [inToken, setInToken] = useState("")

  useEffect(() => {
    if (!repository || repository.folder_id !== folderID) repoGet(prjID, folderID)
    // eslint-disable-next-line
  }, [folderID, prjID])

  if (!repository) return <Loader />
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
    const consumerKey = "xckDCgTDkpEAtWnfYe"
    const response_type = "code"
    localStorage.setItem("oauth_callback_folder", folderID)
    localStorage.setItem("oauth_callback_save_id", prjID)
    const redirectTo = `https://bitbucket.org/site/oauth2/authorize?client_id=${consumerKey}&response_type=${response_type}`
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
      </div>
    </div>
  )
}

export default OptionsFolderGit
