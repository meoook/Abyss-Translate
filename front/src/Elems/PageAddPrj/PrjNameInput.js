import React from "react"
import { findIconChars } from "../componentUtils"

export const PrjNameInput = ({ shadow, setShadow }) => {
  const setIconChars = (event) => {
    setShadow({
      ...shadow,
      name: event.target.value,
      icon_chars: findIconChars(event.target.value.trim()),
    })
  }
  const changeIconChars = (event) => {
    setShadow({ ...shadow, icon_chars: event.target.value })
  }

  return (
    <div>
      <label>Введите название проекта или игры</label>
      <div>
        <input
          className='m-1'
          type='text'
          onChange={setIconChars}
          value={shadow.name}
          autoFocus={true}
          maxLength={50}
        />
      </div>
      <label>2 буквы для иконки в меню</label>
      <div className='row center'>
        <div className='input-short'>
          <input
            className='m-1'
            type='text'
            onChange={changeIconChars}
            value={shadow.icon_chars}
            maxLength={2}
            minLength={2}
          />
        </div>
        <div className='input-like input-short mh-3 t-center'>
          {shadow.icon_chars ? shadow.icon_chars : <>&nbsp;</>}
        </div>
      </div>
    </div>
  )
}

export default PrjNameInput
