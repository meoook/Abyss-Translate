import React, { useContext, useState, useEffect } from "react"

import AppContext from "../../context/application/appContext"

import LanguageSelector from "../AppComponents/LanguageSelector"
import Toggler from "../AppComponents/Toggler"

const TranslateMenu = ({
  langOrig,
  langTrans,
  setLangOrig,
  setLangTrans,
  same,
  setSame,
  noSame,
  setNoSame,
  noTrans,
  setNoTrans,
  like,
  setLike,
  searchText,
  setSearchText,
}) => {
  const { translates } = useContext(AppContext)
  const [original, setOriginal] = useState([])
  const [translate, setTransate] = useState([])
  const [input, setInput] = useState("")

  useEffect(() => {
    if (!translates.translated_set) return
    const filtredLangs = translates.translated_set.filter((item) => item.finished).map((item) => item.language)
    if (filtredLangs.length) setOriginal([...filtredLangs, translates.lang_orig])
    setTransate(translates.translated_set.filter((item) => item.language !== langOrig).map((itm) => itm.language))
  }, [translates, langOrig])

  const searchOnBlur = (e) => {
    setSearchText(input.trim())
  }
  const searchKeyPress = (e) => {
    if ((e.key = "Enter")) setSearchText(input.trim())
  }

  return (
    <div className='box row mb-2'>
      <div className='col col-3'>
        <div className='row center mb-2'>
          <input type='checkbox' checked={same} onChange={setSame.bind(this, !same)} />
          <label className={`mh-1${same ? " active" : ""}`}>изменять одинаковые</label>
        </div>
        <div className='row center'>
          <input type='checkbox' checked={like} onChange={setLike.bind(this, !like)} disabled />
          <label className={`mh-1${like ? " active" : ""}`}>
            <s>изменять похожие</s>
          </label>
        </div>
      </div>
      <div className='col col-4'>
        <div className='row center mb-2'>
          <Toggler val={noSame} setVal={setNoSame} />
          <label className={`mh-1${noSame ? " active" : ""}`}>не показывать одинаковые</label>
        </div>
        <div className='row center'>
          <Toggler val={noTrans} setVal={setNoTrans} />
          <label className={`mh-1${like ? " active" : ""}`}>не показывать переведенные</label>
        </div>
      </div>

      <div className='col col-5'>
        <div className='row'>
          <div className='t-small'>
            <input
              type='text'
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onBlur={searchOnBlur}
              onKeyPress={searchKeyPress}
              className='input'
            />
          </div>
        </div>
        <div className='row'>
          <div className='col col-6'>
            <div className='ml-0 t-small'>Язык оригиналов</div>
            <LanguageSelector selected={langOrig} setSelected={setLangOrig} langArr={original} />
          </div>
          <div className='col col-6'>
            <div className='ml-0 t-small'>Язык для переводов</div>
            <LanguageSelector selected={langTrans} setSelected={setLangTrans} langArr={translate} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default TranslateMenu
