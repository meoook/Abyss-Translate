import React, { useState, useEffect } from "react"

const InputMultiField = ({
  setValues = () => {},
  values = [],
  placeholder = ". . .",
  options = [],
  isDisabled = false,
  isMulti = false,
  isShort = false,
}) => {
  const [active, setActive] = useState(false)
  const [input, setInput] = useState("")
  const [search, setSearch] = useState()
  // UTILS
  useEffect(() => {
    window.addEventListener("click", handleMouseOver)
    setSearch(options.filter((item) => !values.includes(item.id)))
    return () => {
      window.removeEventListener("click", handleMouseOver)
    }
    // eslint-disable-next-line
  }, [])
  // useEffect(() => {
  //   const allowOptions = options.filter((item) => !values.includes(item.id))
  //   setSearch(allowOptions.filter((item) => item.name.toLowerCase().includes(input.trim().toLowerCase())))
  // })
  // HANDLERS
  const handleInput = (event) => {
    const input = event.target.value
    setInput(input)
    const allowOptions = options.filter((item) => !values.includes(item.id))
    if (input.trim())
      setSearch(allowOptions.filter((item) => item.name.toLowerCase().includes(input.trim().toLowerCase())))
    else setSearch(allowOptions)
  }
  const handleClick = (event) => {
    // if (active) event.stopPropagation()
    if (isDisabled || !options.length) return
    setSearch(options.filter((item) => !values.includes(item.id)))
    setTimeout(() => {
      setActive(!active)
    }, 0)
    // else setActive(!active)
  }
  const handleClickItem = (id) => {
    const item = options.find((opt) => opt.id === id)
    if (!isMulti) {
      setValues([item.id])
      setSearch(options.filter((item) => item.id !== id))
      setActive(false)
    } else {
      setValues([...values, item.id].filter((item, index, arr) => arr.indexOf(item) === index))
      setSearch(options.filter((item) => !values.includes(item.id) && item.id !== id))
    }
    setInput("")
  }
  const handleMouseOver = () => {
    setInput("")
    setActive(false)
  }
  const handleReset = (event) => {
    event.stopPropagation()
    setValues([])
    setSearch(options)
    setInput("")
  }
  const handleRemoveValue = (id) => {
    setValues(values.filter((item) => item !== id))
    setSearch(options.filter((item) => !values.includes(item.id) || item.id === id))
  }
  // COMPONENTS
  const ResetBtn = () => {
    if (isDisabled || !values.length) return <></>
    return (
      <div className='input-ico' onClick={handleReset}>
        &times;
      </div>
    )
  }
  const PHolder = () => {
    if (input || (!isMulti && !active && values.length)) return <></>
    if (isMulti || !active || !values.length) return <div className='input-placeholder'>{placeholder}</div>
    const selectedLang = options.find((item) => item.id === values[0])
    return <div className='input-placeholder'>{selectedLang ? selectedLang.name : <>&nbsp;</>}</div>
  }
  const CurrentValues = () => {
    if (!values.length || (!isMulti && active)) return <></>
    const selectedLang = options.find((item) => item.id === values[0])
    if (!isMulti) return <div className='input-current'>{selectedLang ? selectedLang.name : <>&nbsp;</>}</div>
    return (
      <div className='input-current'>
        {options
          .filter((item) => values.includes(item.id))
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
        disabled={!options.length || isDisabled}>
        <CurrentValues />
        <div className='input-in'>
          <div className={input ? "" : "hidden-in"}>
            {active && <input type='text' value={input} onChange={handleInput} autoFocus={true} />}
          </div>
          <PHolder />
        </div>
        <ResetBtn />
        {options.length && <div className='input-ico'>></div>}
      </div>
      {active && <InputDropDown />}
    </div>
  )
}
export default InputMultiField
