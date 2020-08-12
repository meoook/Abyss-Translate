import React, { useState } from "react"

export const PrjRepositoriesAdd = ({ shadow, setShadow }) => {
  const [input, setInput] = useState("")
  const onChange = (event) => {
    setInput(event.target.value)
  }

  const repoUrlAdd = (event) => {
    // TODO: Проверка на существование Репозитория при добавлении

    if (input.trim()) {
      setShadow({ ...shadow, repositories: [...shadow.repositories, input.trim()] })
      setInput("")
    }
  }

  return (
    <React.Fragment>
      <div>
        Что бы не скачивать файлы из "Системы переводов" можно настроить синхронизацию с GIT репозиторием
        <b>(?) как это работает</b>
      </div>
      <div>
        <div>
          Введите URL на GIT репозиторий для добавление в список
          <b>(!) доступ</b>
        </div>
        <div className='input-group'>
          <input
            type='text'
            value={input}
            onChange={onChange}
            onKeyDown={(e) => {
              if (e.key === "Enter") repoUrlAdd()
            }}
            autoFocus={true}
          />
          <button className='btn green' onClick={repoUrlAdd} disabled={!input ? true : false}>
            add
          </button>
        </div>
      </div>
      <div>Данный пункт можно пропустить и добавить GIT репозитории позднее</div>
    </React.Fragment>
  )
}
export default PrjRepositoriesAdd
