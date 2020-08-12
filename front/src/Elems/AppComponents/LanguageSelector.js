import React, { useContext, useState } from "react"
import AppContext from "../../context/application/appContext"
import { IcoLang } from "../icons"
import { useEffect } from "react"

const LanguageSelector = ({ selected, setSelected, langArr = [] }) => {
  const { languages } = useContext(AppContext)
  const [open, setOpen] = useState(false)
  const choices = languages.filter((item) => langArr.includes(item.id) && item.id !== selected)
  const current = languages.find((item) => item.id === selected)

  useEffect(() => {
    window.addEventListener("click", handleLooseFocus)
    return () => {
      window.removeEventListener("click", handleLooseFocus)
    }
    // eslint-disable-next-line
  }, [])

  const handleLooseFocus = () => {
    setOpen(false)
  }
  const handleTrigger = (event) => {
    event.stopPropagation()
    if (!choices.length) return
    setOpen(!open)
  }

  return (
    <div className={`custom-select${open ? " open" : ""}`}>
      <div className='custom-select-trigger' onClick={handleTrigger}>
        {current ? (
          <span>
            <i className='bd'>
              <IcoLang language={current.name} />
            </i>
            {current.name}
          </span>
        ) : (
          <></>
        )}
        {choices.length > 0 && <div className='custom-select-arrow'></div>}
      </div>
      <div className='custom-options'>
        {choices.map((lang) => (
          <div key={lang.id} className='custom-option' onClick={setSelected.bind(this, lang.id)}>
            <span>
              <i className='bd'>
                <IcoLang language={lang.name} />
              </i>
              {lang.name}
            </span>
            <span>&nbsp;</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default LanguageSelector
