import React, { useContext, useState, useEffect } from "react"

import AppContext from "../../context/application/appContext"

import { IcoGet } from "../icons"
import LanguageSelector from "../AppComponents/LanguageSelector"

const TranslateMenu = ({ langOrig, langTrans, setLangOrig, setLangTrans, same, setSame, noTrans, setNoTrans }) => {
  const { translates } = useContext(AppContext)
  const [original, setOriginal] = useState([])
  const [translate, setTransate] = useState([])

  useEffect(() => {
    if (!translates.translate_to) return
    const filtredLangs = translates.translated_set.filter((item) => item.finished).map((item) => item.language)
    setOriginal([...filtredLangs, translates.lang_orig])
    setTransate(translates.translate_to.filter((item) => item !== langOrig))
  }, [translates, langOrig])

  return (
    <div className='input-group m-2'>
      <h3 className='input-like'>{`${translates.name} элементов ${translates.items_count} слов ${translates.words}`}</h3>
      <button className={`btn${same ? " active" : ""}`} onClick={setSame}>
        same
      </button>
      <button className='btn' disabled={true}>
        like
      </button>
      <button className={`btn${noTrans ? " active" : ""}`} onClick={setNoTrans}>
        no trans
      </button>
      <div className='row'>
        <div className='col col-6'>
          <LanguageSelector selected={langOrig} setSelected={setLangOrig} langArr={original} />
        </div>
        <div className='col col-6'>
          <LanguageSelector selected={langTrans} setSelected={setLangTrans} langArr={translate} />
        </div>
      </div>
      <button className='btn btn-icon'>
        <i>
          <IcoGet name='cloudin' />
        </i>
      </button>
    </div>
  )
}

export default TranslateMenu
