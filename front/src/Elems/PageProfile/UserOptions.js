import React from "react"
// import GitUrls from "./GitUrls"
// import GitUploadUrl from "./GitUploadUrl"
import UploadFiles from "./UploadFiles"

const UserOptions = (props) => {
  return (
    <div>
      <UploadFiles />
      <h3>Загрузить с GIT</h3>
      <div>Добавить URL для загрузки файлов из репозитория GIT (можно кнопочку + чтоб несколько)</div>
      {/* <GitUrls urls={options.gitUrls} /> */}
      <div>
        Обратите внимание что доступ к репозиторию должен быть public или предоставлен доступ для abbys@gitlab.com
      </div>
      <hr />
      <h3>Хранение переведенных файлов</h3>
      {/* <GitUploadUrl url={options.gitUploadUrl} gitSave={options.gitSave} /> */}
    </div>
  )
}

export default UserOptions
