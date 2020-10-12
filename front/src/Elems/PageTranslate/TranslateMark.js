import React, { useState, useEffect, useContext } from "react"
import AppContext from "../../context/application/appContext"

const TranslateMark = ({ mark, langOrig, langTrans, same, setActive }) => {
  const originalDisplay = mark.translates_set.find((translate) => translate.language === langOrig)
  const { transChange } = useContext(AppContext)
  const [inputVal, setInputVal] = useState("")
  const [changed, setChanged] = useState(false)
  const [transObj, setTransObj] = useState(null)

  useEffect(() => {
    const translateDisplay = mark.translates_set.find((translate) => translate.language === langTrans)
    setTransObj(translateDisplay)
    if (translateDisplay) setInputVal(translateDisplay.text)
    else setInputVal("")
  }, [mark, langTrans])

  const handleChange = (event) => {
    setChanged(true)
    setInputVal(event.target.value)
  }
  const changeTranslate = (event) => {
    if (!changed) return
    setChanged(false)
    if (same) transChange(mark.id, langTrans, inputVal, mark.md5sum)
    else transChange(mark.id, langTrans, inputVal)
  }
  const handleSelect = (event) => {
    // setActive(mark.id)
    if (transObj) setActive(transObj.id)
    else setActive(null)
  }

  return (
    <div className='card-translate m-1' onClick={handleSelect}>
      <div className='card-translate-head'>
        <div>
          ID&nbsp;{mark.id} {transObj && transObj.translator && `перевел ${transObj.translator}`}
        </div>
        <div>слов&nbsp;{mark.words}</div>
      </div>
      <>
        <div className='card-translate-content'>
          {originalDisplay ? originalDisplay.text : `System error ${mark.id}`}
        </div>
        <div className='card-translate-input'>
          <input type='textaria' value={inputVal} onChange={handleChange} onBlur={changeTranslate} />
        </div>
      </>
    </div>
  )
}

export default TranslateMark
