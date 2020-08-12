import React, { useState, useEffect } from "react"
import { IcoGet } from "../icons"

const InputCkeckField = ({ setValue = () => {}, value = "", ico = "", big = false, search = [] }) => {
  const [input, setInput] = useState(value)
  const [error, setError] = useState("")

  useEffect(() => {
    setInput(value)
  }, [value])
  // Utils
  const searchVal = (val) => search.find((item) => item.name === val)
  const checkErrors = (val) => {
    const inCheck = val.trim()
    if (!inCheck) return setError("название не может быть пустым")
    if (searchVal(inCheck)) return setError("такое название уже есть")
    setError("")
    if (inCheck === value) return false
    return true
  }
  // Handlers
  const handleInput = (event) => {
    setInput(event.target.value)
    checkErrors(event.target.value)
  }
  const checkAndSave = () => {
    if (checkErrors(input)) setValue(input.trim())
    else setInput(value)
    setError("")
  }

  return (
    <div className='input-inline' onBlur={checkAndSave}>
      <input type='text' value={input} onChange={handleInput} className={big ? "in-big" : ico ? "pl-4" : null} />
      {ico && (
        <i className={big ? "big" : null}>
          <IcoGet name={ico} />
        </i>
      )}
      <div className='input-underrow'></div>
      {error && <div className='input-error t-small'>{error}</div>}
    </div>
  )
}

export default InputCkeckField
