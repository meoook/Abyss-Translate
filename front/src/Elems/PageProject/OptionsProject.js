import React, { useState, useEffect, useContext } from "react"

import InputCkeckField from "../AppComponents/InputCheckField"
import AppContext from "../../context/application/appContext"
import InputMultiField from "../AppComponents/InputMultiField"

// UTILS
const langOrigValues = (lang) => (lang ? [lang] : [])
const getPrjData = (proj) => {
  return { save_id: proj.save_id, name: proj.name, icon_chars: proj.icon_chars }
}

const OptionsProject = ({ prjObj }) => {
  const { projects, prjUpdate, prjRemove, languages } = useContext(AppContext)
  const [iconChars, setIconChars] = useState("")
  const [langTrans, setLangTrans] = useState([])
  const [search, setSearch] = useState([]) // User projects name list to filter\error when input

  useEffect(() => {
    if (prjObj) {
      setLangTrans(languages.filter((item) => item.id !== prjObj.lang_orig))
      setIconChars(prjObj.icon_chars)
      setSearch(
        projects.reduce((result, item) => {
          if (item.id === prjObj.id) return result
          else return [...result, { name: item.name }] // Need only name here
        }, [])
      )
    }
  }, [prjObj, projects, languages])

  // Handlers
  const saveName = (name) => {
    if (name !== prjObj.name) prjUpdate({ save_id: prjObj.save_id, name, icon_chars: prjObj.icon_chars })
  }
  const changeIconChars = (event) => {
    setIconChars(event.target.value)
  }
  const saveIconChars = (event) => {
    if (iconChars.length !== 2) return // setError("недостаточной длинны")
    if (iconChars !== prjObj.icon_chars)
      prjUpdate({ save_id: prjObj.save_id, name: prjObj.name, icon_chars: iconChars })
  }
  const saveLangOrig = (lang) => {
    prjUpdate({
      ...getPrjData(prjObj),
      lang_orig: lang[0] ? lang[0] : null,
      translate_to: prjObj.translate_to.filter((item) => item !== lang[0]),
    })
  }
  const saveLangTrans = (langs) => {
    // Choise field - no need to check
    prjUpdate({ ...getPrjData(prjObj), translate_to: langs })
  }

  return (
    <div className='expl row mt-2'>
      <div className='col col-7 column'>
        <div className='table-head'>
          <div>Последние изменения файлов</div>
          <div className='color-error ml-2'>(в стадии разработке)</div>
        </div>
        <div className='scroll-y paginate column m-1'>
          <div className='table-line m-0'>
            <div className='col col-3'>GameName</div>
            <div className='col col-3'>UserName</div>
            <div className='col col-3'>FileName</div>
            <div className='col col-3'>Date</div>
          </div>
          <div className='table-line m-0'>
            <div className='col col-3'>LineStrike</div>
            <div className='col col-3'>meok</div>
            <div className='col col-3'>Ru.po</div>
            <div className='col col-3'>28.01.20</div>
          </div>
        </div>
      </div>

      <div className='col col-5 column'>
        <div className='table-head ml-3'>Настройки</div>

        <div className='m-3 ml-3'>
          <InputCkeckField value={prjObj.name} setValue={saveName} ico='worko' big={true} search={search} />
        </div>

        <div className='scroll-y paginate column ml-3'>
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
          <InputMultiField values={langOrigValues(prjObj.lang_orig)} setValues={saveLangOrig} options={languages} />
          <div className='m-1'>Языки необходимых переводов</div>
          <InputMultiField
            values={prjObj.translate_to}
            setValues={saveLangTrans}
            options={langTrans}
            isMulti={true}
            isShort={true}
          />
          <div className='m-3'>&nbsp;</div>
        </div>

        <div className='fix-bot column ml-3'>
          <hr />
          <div className='row center justify'>
            <div>&nbsp;</div>
            <div>
              <button className='btn red' onClick={prjRemove.bind(this, prjObj.save_id)}>
                Удалить игру
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OptionsProject
