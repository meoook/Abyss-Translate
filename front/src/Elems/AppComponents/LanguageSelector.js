import React, { useContext, useState } from "react"
import AppContext from "../../context/application/appContext"
import { IcoLang } from "../icons"
import { useEffect } from "react"

const LanguageSelector = ({ selected, setSelected, langArr = [] }) => {
  const { languages } = useContext(AppContext)
  const [open, setOpen] = useState(false)
  const [choices, setChoices] = useState([])

  useEffect(() => {
    window.addEventListener("click", handleLooseFocus)
    return () => {
      window.removeEventListener("click", handleLooseFocus)
    }
    // eslint-disable-next-line
  }, [])

  useEffect(() => {
    if (langArr) setChoices(languages.filter((item) => langArr.includes(item.id) && item.id !== selected))
    // eslint-disable-next-line
  }, [languages, langArr, selected])

  const handleLooseFocus = () => {
    setOpen(false)
  }
  const handleTrigger = (event) => {
    event.stopPropagation()
    if (!choices.length) return
    setOpen(!open)
  }

  return (
    <div className={`lang-select${open ? " open" : ""}`}>
      <div className='lang-select-trigger' onClick={handleTrigger}>
        <span>
          <IcoLang language={selected} displayFull={true} className='bd' />
        </span>

        {choices.length > 0 && <div className='lang-select-arrow'></div>}
      </div>
      {Boolean(choices) && (
        <LanguageSelectorDropdown setSelected={setSelected} loseFocus={handleLooseFocus} choices={choices} />
      )}
    </div>
  )
}

export default LanguageSelector

const LanguageSelectorDropdown = ({ choices, setSelected, loseFocus }) => {
  useEffect(() => {
    window.addEventListener("click", loseFocus)
    return () => {
      window.removeEventListener("click", loseFocus)
    }
    // eslint-disable-next-line
  }, [])

  return (
    <div className='lang-select-options'>
      {choices.map((lang) => (
        <div key={lang.id} className='lang-select-option' onClick={setSelected.bind(this, lang.id)}>
          <span>
            <IcoLang language={lang.id} displayShort={true} />
          </span>
          <span>&nbsp;</span>
        </div>
      ))}
    </div>
  )
}
