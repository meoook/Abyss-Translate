import React, { useContext, useState, useEffect } from "react"

import AppContext from "../../context/application/appContext"

import InputCkeckField from "../AppComponents/InputCheckField"
import InputMultiField from "../AppComponents/InputMultiField"

const OptionsProject = ({ project }) => {
  // TODO: Отображать ошибки при неправильном вводе
  const { prjUpdate, prjRemove, languages, user } = useContext(AppContext)
  const [iconChars, setIconChars] = useState(project.icon_chars)
  const [langTransOptions, setTransSelect] = useState(languages.filter((item) => item.id !== project.lang_orig))

  useEffect(() => {
    setTransSelect(languages.filter((item) => item.id !== project.lang_orig))
    setIconChars(project.icon_chars)
  }, [project, languages])

  // User projects name list to filter when input
  const search = user.projects.reduce((res, item) => {
    if (item.save_id === project.save_id) return res
    else return [...res, { name: item.name }] // Need only name here
  }, [])
  // Utils
  const getPrjData = (proj) => {
    return { save_id: proj.save_id, name: proj.name, icon_chars: proj.icon_chars }
  }
  const langOrigValues = (lang) => (lang ? [lang] : [])
  // Handlers
  const saveName = (name) => {
    // TODO: Check name
    prjUpdate({ save_id: project.save_id, name, icon_chars: project.icon_chars })
  }
  const changeIconChars = (event) => {
    setIconChars(event.target.value)
  }
  const saveIconChars = (event) => {
    // TODO:Check icon chars
    if (iconChars.length !== 2) return // setError("недостаточной длинны")
    prjUpdate({ save_id: project.save_id, name: project.name, icon_chars: iconChars })
  }
  const saveLangOrig = (lang) => {
    // Choise field - no need to check
    // if (lang[0])
    prjUpdate({
      ...getPrjData(project),
      lang_orig: lang[0] ? lang[0] : null,
      translate_to: project.translate_to.filter((item) => item !== lang[0]),
    })
  }
  const saveLangTrans = (langs) => {
    // Choise field - no need to check
    prjUpdate({ ...getPrjData(project), translate_to: langs })
  }

  return (
    <>
      <div className='m-3'>
        <div className='mh-2 m-3'>
          <InputCkeckField value={project.name} setValue={saveName} ico='worko' big={true} search={search} />
        </div>
        <div className='explorer-scroll'>
          <div className='mh-2 p-0'>
            <label>2 буквы для иконки в меню</label>
            <div className='row center'>
              <div className='input-short'>
                <input
                  className='m-1'
                  type='text'
                  onChange={changeIconChars}
                  value={iconChars}
                  maxLength={2}
                  minLength={2}
                  onBlur={saveIconChars}
                />
              </div>
              <div className='input-like input-short mh-3 t-center'>{iconChars ? iconChars : <>&nbsp;</>}</div>
            </div>
            <div className='m-1'>Язык оригинала для новых файлов</div>
            <InputMultiField values={langOrigValues(project.lang_orig)} setValues={saveLangOrig} options={languages} />
            <div className='m-1'>Языки необходимых переводов</div>
            <InputMultiField
              values={project.translate_to}
              setValues={saveLangTrans}
              options={langTransOptions}
              isMulti={true}
              isShort={true}
            />
            <hr />
          </div>
          <div className='m-3'>&nbsp;</div>
        </div>
        <div className='fix-bot column'>
          <hr />
          <div className='row center justify mh-2 mb-0'>
            <div>&nbsp;</div>
            <div>
              <button className='btn red' onClick={prjRemove.bind(this, project.save_id)}>
                Удалить проект
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default OptionsProject
