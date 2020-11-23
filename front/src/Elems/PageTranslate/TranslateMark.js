import React, { useState, useEffect, useContext } from "react"
import AppContext from "../../context/application/appContext"

const TranslateMark = ({ mark, langOrig, langTrans, same, setActive, activeID }) => {
  const [displayContext, setDisplayContext] = useState(false)

  return (
    <div className='card-translate m-1'>
      <div
        className='card-translate-head'
        onClick={() => {
          setDisplayContext(!displayContext)
        }}>
        <div>ID&nbsp;метки&nbsp;{mark.id}</div>
        <div>слов&nbsp;{mark.words}</div>
      </div>
      {displayContext && <div className='mh-2'>{mark.context}</div>}
      <div>
        {mark.markitem_set.map((markitem) => (
          <TranslateMarkItem
            key={markitem.item_number}
            item={markitem}
            langOrig={langOrig}
            langTrans={langTrans}
            setActive={setActive}
            activeID={activeID}
            same={same}
          />
        ))}
      </div>
    </div>
  )
}

export default TranslateMark

const TranslateMarkItem = ({ item, langOrig, langTrans, same, setActive, activeID }) => {
  const originalDisplay = item.translate_set.find((translate) => translate.language === langOrig)
  const { transChange } = useContext(AppContext)
  const [inputVal, setInputVal] = useState("")
  const [changed, setChanged] = useState(false) // Not to send empty req
  const [transObj, setTransObj] = useState(null)

  useEffect(() => {
    const translateDisplay = item.translate_set.find((translate) => translate.language === langTrans)
    setTransObj(translateDisplay)
    if (translateDisplay) setInputVal(translateDisplay.text)
    else setInputVal("")
  }, [item, langTrans])

  const handleChange = (event) => {
    setChanged(true)
    setInputVal(event.target.value)
  }
  const changeTranslate = (event) => {
    if (!changed) return
    setChanged(false)
    if (same) transChange(transObj.id, inputVal, item.md5sum)
    else transChange(transObj.id, inputVal)
  }
  const handleSelect = (event) => {
    // setActive(mark.id)
    if (transObj) setActive(transObj.id)
    else setActive(null)
  }
  const handleWarningClick = (event) => {
    transChange(transObj.id, transObj.text)
  }

  if (!Boolean(originalDisplay) || !Boolean(transObj)) return null
  return (
    <div className={`card-translate-item${activeID === transObj.id ? " active" : ""}`} onClick={handleSelect}>
      <div className='col col-6'>
        <div className='card-translate-item-head'>
          <div>ID&nbsp;{originalDisplay.id}</div>
          <div>слов&nbsp;{item.words}</div>
        </div>
        <div className='card-translate-content'>
          {originalDisplay ? originalDisplay.text : `System error ${item.id}`}
        </div>
      </div>
      <div className='col col-6'>
        <div className='card-translate-item-head'>
          <div>ID&nbsp;{transObj.id}</div>
          {Boolean(transObj.warning) ? (
            <div className='color-warning' onClick={handleWarningClick}>
              {transObj.warning}
            </div>
          ) : Boolean(transObj.translator) ? (
            <div>{`перевел ${transObj.translator}`}</div>
          ) : (
            <div>&nbsp;</div>
          )}
        </div>
        <div className='card-translate-input'>
          <textarea
            // wrap='soft'
            // rows='auto'
            value={inputVal}
            onChange={handleChange}
            onBlur={changeTranslate}
            placeholder='текст перевода'
          />
        </div>
      </div>
    </div>
  )
}
