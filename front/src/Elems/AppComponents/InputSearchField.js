import React, { useState, useEffect } from "react"

const InputSearchField = ({ val, setVal, label = "Введите значение", options = [] }) => {
  // state
  const [choices, setChoices] = useState([])
  const [input, setInput] = useState("")
  const [displayChoices, setDisplaylChoices] = useState(false)

  useEffect(() => {
    window.addEventListener("click", handleMouseOver)
    return () => {
      window.removeEventListener("click", handleMouseOver)
    }
    // eslint-disable-next-line
  }, [])

  useEffect(() => {
    setInput(val)
  }, [val])

  useEffect(() => {
    setChoices(options.filter((item) => item !== input && item.length >= input.length))
  }, [input, options])

  // handlers
  const handleClick = (event) => {
    event.stopPropagation()
    setDisplaylChoices(!displayChoices)
  }
  const handleMouseOver = (event) => {
    // TODO: Remake onBlur
    setDisplaylChoices(false)
  }

  const handleInput = (e) => {
    if (!displayChoices) setDisplaylChoices(true)
    const value = e.target.value
    setInput(value)
    setVal(value)
  }

  const optSelect = (value, event) => {
    event.stopPropagation()
    setDisplaylChoices(false)
    setInput(value)
    setVal(value)
  }

  const resetBtn = (event) => {
    event.stopPropagation()
    setInput("")
    setVal("")
  }

  // elems
  const dropdown =
    !displayChoices || !choices.length ? null : (
      <div className='md-input-choices'>
        {choices.map((item) => (
          <div key={item} className={item === val ? "active" : null} onClick={optSelect.bind(this, item)}>
            {item}
          </div>
        ))}
      </div>
    )
  // if statement
  const btnsClass = () => {
    if (val && choices.length) return "md-input-btns icons"
    if (val || choices.length) return "md-input-btns icon"
    return "md-input-btns"
  }

  return (
    <div className='md-input' onClick={handleClick}>
      <div className='md-input-wrapper'>
        <div className='md-input-root icons'>
          <input tabIndex='0' type='text' autoComplete='off' value={input} onChange={handleInput} required />
          <label>{label}</label>
          <div className={btnsClass()}>
            {input ? (
              <button tabIndex='-1' className='md-input-btns-x' onClick={resetBtn}>
                <span className='md-input-icons'>
                  <svg focusable='false' viewBox='0 0 24 24' aria-hidden='true'>
                    <path d='M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z'></path>
                  </svg>
                </span>
              </button>
            ) : null}
            {choices.length > 0 && (
              <button
                tabIndex='-1'
                className={`md-input-btns-m${displayChoices ? " rotate" : ""}`}
                onClick={setDisplaylChoices.bind(this, !displayChoices)}>
                <span className='md-input-icons'>
                  <svg focusable='false' viewBox='0 0 24 24' aria-hidden='true'>
                    <path d='M7 10l5 5 5-5z'></path>
                  </svg>
                </span>
              </button>
            )}
          </div>
          <fieldset>
            <legend>
              <span>{label}</span>
            </legend>
          </fieldset>
        </div>
        {dropdown}
      </div>
    </div>
  )
}

export default InputSearchField
