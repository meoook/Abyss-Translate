import React, { useState, useEffect } from "react"

const InputChoiseField = ({ setValue, value = null, placeholder = ". . .", choises = [], isDisabled = false }) => {
  const [active, setActive] = useState(false)
  const [input, setInput] = useState("")
  const [search, setSearch] = useState()

  useEffect(() => {
    window.addEventListener("click", handleMouseOver)
    setSearch(choises.filter((item) => !value.includes(item.id)))
    return () => {
      window.removeEventListener("click", handleMouseOver)
    }
    // eslint-disable-next-line
  }, [])

  // HANDLERS
  const handleMouseOver = () => {
    setInput("")
    setActive(false)
  }

  const handleInput = (event) => {
    const input = event.target.value
    setInput(input)
    const allowChoises = choises.filter((item) => !value.includes(item.id))
    if (input.trim())
      setSearch(allowChoises.filter((item) => item.name.toLowerCase().includes(input.trim().toLowerCase())))
    else setSearch(allowChoises)
  }

  const handleClick = (event) => {
    // if (active) event.stopPropagation()
    if (isDisabled || !choises.length) return
    setSearch(choises.filter((item) => !value.includes(item.id)))
    setTimeout(() => {
      setActive(!active)
    }, 0)
    // else setActive(!active)
  }

  const handleClickItem = (id) => {
    const item = choises.find((opt) => opt.id === id)
    if (!isMulti) {
      setValues([item.id])
      setSearch(choises.filter((item) => item.id !== id))
      setActive(false)
    } else {
      setValues([...value, item.id].filter((item, index, arr) => arr.indexOf(item) === index))
      setSearch(choises.filter((item) => !value.includes(item.id) && item.id !== id))
    }
    setInput("")
  }

  const handleReset = (event) => {
    event.stopPropagation()
    setValues([])
    setSearch(choises)
    setInput("")
  }
  const handleRemoveValue = (id) => {
    setValues(value.filter((item) => item !== id))
    setSearch(choises.filter((item) => !value.includes(item.id) || item.id === id))
  }
  // COMPONENTS
  const ResetBtn = () => {
    if (isDisabled || !value.length) return <></>
    return (
      <div className='input-ico' onClick={handleReset}>
        &times;
      </div>
    )
  }
  const PHolder = () => {
    if (input || (!isMulti && !active && value.length)) return <></>
    if (isMulti || !active || !value.length) return <div className='input-placeholder'>{placeholder}</div>
    const selectedLang = choises.find((item) => item.id === value[0])
    return <div className='input-placeholder'>{selectedLang ? selectedLang.name : <>&nbsp;</>}</div>
  }
  const CurrentValues = () => {
    if (!value.length || (!isMulti && active)) return <></>
    const selectedLang = choises.find((item) => item.id === value[0])
    if (!isMulti) return <div className='input-current'>{selectedLang ? selectedLang.name : <>&nbsp;</>}</div>
    return (
      <div className='input-current'>
        {choises
          .filter((item) => value.includes(item.id))
          .map((val) => (
            <span className='input-value' key={val.id}>
              <span className='ph-0'>
                {!isShort ? val.name : val.short_name.charAt(0).toUpperCase() + val.short_name.slice(1).toLowerCase()}
              </span>
              {!isDisabled ? (
                <span
                  className='input-value-remove'
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRemoveValue(val.id)
                  }}>
                  &times;
                </span>
              ) : (
                <></>
              )}
            </span>
          ))}
      </div>
    )
  }
  const InputDropDown = () => {
    if (!search || !search.length) return <></>
    return (
      <div className='input-dropdown'>
        <div>
          {search.map((item) => (
            <div
              key={item.id}
              className='input-dropdown-item'
              value={item.id}
              onClick={(e) => {
                e.stopPropagation()
                handleClickItem(item.id)
              }}>
              {item.name}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className='input'>
      <div
        className={`input-field${active ? " active" : ""}`}
        onClick={handleClick}
        disabled={!choises.length || isDisabled}>
        <CurrentValues />
        <div className='input-in'>
          <div className={input ? "" : "hidden-in"}>
            {active && <input type='text' value={input} onChange={handleInput} autoFocus={true} />}
          </div>
          <PHolder />
        </div>
        <ResetBtn />
        {choises.length && <div className='input-ico'>></div>}
      </div>
      {active && <InputDropDown />}
    </div>
  )
}
export default InputChoiseField
