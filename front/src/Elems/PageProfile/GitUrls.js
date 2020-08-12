import React, { useState } from "react"

export default function GitUrls({ urls }) {
  const [gitUrls, setGitUrls] = useState(urls)
  const handleAddUrl = () => {
    if (inputUrl.trim().length > 0) {
      setGitUrls([...gitUrls, inputUrl.trim()])
      setInputUrl("")
    }
  }
  const handleRemoveUrl = (url) => {
    setGitUrls(gitUrls.filter((el) => el !== url))
  }

  const [inputUrl, setInputUrl] = useState("")
  const handleInputUrl = (event) => {
    setInputUrl(event.target.value)
  }

  return (
    <div className='git-urls'>
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
      {gitUrls.map((item) => (
        <div key={item} className='url row'>
          <div>https://{item}</div>
          <button
            className='btn red input-ok'
            onClick={() => {
              handleRemoveUrl(item)
            }}>
            &times;
          </button>
        </div>
      ))}
    </div>
  )
}
