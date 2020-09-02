import React, { useState, useEffect, useContext } from "react"
import AppContext from "../../context/application/appContext"

const TranslateMark = ({ mark, langOrig, langTrans, same, setActive }) => {
  const originalDisplay = mark.translates_set.find((translate) => translate.language === langOrig)
  const { transChange } = useContext(AppContext)
  const [inputVal, setInputVal] = useState("")
  const [changed, setChanged] = useState(false)

  useEffect(() => {
    const translateDisplay = mark.translates_set.find((translate) => translate.language === langTrans)
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

  return (
    <div className='input-group m-1'>
      {!originalDisplay ? (
        <div className='input-like'>System error {mark.id}</div>
      ) : (
        <>
          <div className='col col-6 input-like'>{originalDisplay.text}</div>
          <input
            className='col col-6'
            type='textaria'
            value={inputVal}
            onChange={handleChange}
            onBlur={changeTranslate}
          />
        </>
      )}
    </div>
  )
}

export default TranslateMark
