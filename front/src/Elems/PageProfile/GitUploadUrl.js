import React, { useState } from "react"

export default function GitUploadUrl({ url, gitSave }) {
  const [saveGit, setSaveGit] = useState(gitSave)
  const toggleSaveGit = () => {
    setSaveGit(!saveGit)
  }

  const [uploadUrl, setUploadUrl] = useState(url)
  const handleAddUrl = () => {
    if (inputUrl.trim().length > 0) {
      setUploadUrl(inputUrl.trim())
      setInputUrl("")
    }
  }
  const handleRemoveUrl = () => {
    setUploadUrl("")
  }

  const [inputUrl, setInputUrl] = useState("")
  const handleInputUrl = (event) => {
    setInputUrl(event.target.value)
  }

  return (
    <>
      <div className='row center'>
        <input type='checkbox' onChange={toggleSaveGit} checked={saveGit} />
        <div>
          <div>Хранить в репозитории для загрузки файлов</div>
          <div>(например файлы будут размещаться по пути /EN/filename.txt для английского языка)</div>
        </div>
      </div>
      {!uploadUrl && <div>Или укажите ссылку репозитория для хранения перведенных файлов</div>}
      <div className='git-urls'>
        {uploadUrl ? (
          <div className='url row'>
            <div>https://{uploadUrl}</div>
            <button
              className='btn red input-ok'
              onClick={() => {
                handleRemoveUrl()
              }}>
              X
            </button>
          </div>
        ) : (
          <div>
            <input
              type='text'
              value={inputUrl}
              onChange={handleInputUrl}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAddUrl()
              }}
            />
            <button className='btn green input-ok' onClick={handleAddUrl}>
              add
            </button>
          </div>
        )}
      </div>
    </>
  )
}
