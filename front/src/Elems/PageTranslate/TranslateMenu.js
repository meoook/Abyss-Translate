import React, { useContext, useState, useEffect } from "react"

import AppContext from "../../context/application/appContext"

import { IcoGet } from "../icons"
import LanguageSelector from "../AppComponents/LanguageSelector"

const TranslateMenu = ({ langOrig, langTrans, setLangOrig, setLangTrans, same, setSame, noTrans, setNoTrans }) => {
  const { translates } = useContext(AppContext)
  const [original, setOriginal] = useState([])
  const [translate, setTransate] = useState([])

  useEffect(() => {
    if (!translates.translated_set) return
    const filtredLangs = translates.translated_set.filter((item) => item.finished).map((item) => item.language)
    console.log(filtredLangs.length ? "true" : "false")
    if (filtredLangs.length) {
      console.log(filtredLangs.length ? "true1" : "false1")

      setOriginal([...filtredLangs, translates.lang_orig])
      setTransate(translates.translated_set.filter((item) => item !== langOrig))
    } else {
      console.log(filtredLangs.length ? "true2" : "false2")

      setOriginal(["not set"])
      setTransate(["not set"])
    }
  }, [translates, langOrig])

  return (
    <div className='input-group mb-2'>
      <button className={`btn${same ? " active" : ""}`} onClick={setSame}>
        Chg same
      </button>
      <button className='btn icon' disabled={true}>
        Chg like
      </button>
      <button className={`btn small${noTrans ? " active" : ""}`} onClick={setNoTrans}>
        Dply no same
      </button>
      <button className={`btn${noTrans ? " active" : ""}`} onClick={setNoTrans}>
        Dply no trans
      </button>
      <div className='row'>
        <div className='col col-6'>
          <LanguageSelector selected={langOrig} setSelected={setLangOrig} langArr={original} />
        </div>
        <div className='col col-6'>
          <LanguageSelector selected={langTrans} setSelected={setLangTrans} langArr={translate} />
        </div>
      </div>
      <button className='btn btn-disabled' disabled>
        90%
      </button>
    </div>
  )
}

export default TranslateMenu
