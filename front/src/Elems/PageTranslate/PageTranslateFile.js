import React, { useEffect, useContext, useState } from "react"
import { useParams } from "react-router-dom"
import AppContext from "../../context/application/appContext"
import TranslateMenu from "./TranslateMenu"
import TranslateMark from "./TranslateMark"
import Paginator from "../AppComponents/Paginator"
import Loader from "../AppComponents/Loader"

const PageTranslateFile = (props) => {
  // STATE
  const { id } = useParams()
  const { transMarkList, transFileInfo, translates, translatesLoading } = useContext(AppContext)
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(25)
  const [same, setSame] = useState(false)
  const [noTrans, setNoTrans] = useState(0)
  const [langOrig, setLangOrig] = useState(null)
  const [langTrans, setLangTrans] = useState(null)

  useEffect(() => {
    transFileInfo(id, page, size, same, noTrans)
    // eslint-disable-next-line
  }, [id])

  useEffect(() => {
    console.log('Langs', langOrig, langTrans)
    if (!translates.lang_orig) return
    if (!langOrig) setLangOrig(translates.lang_orig)
    if (!langTrans) setLangTrans(translates.translate_to[0]) // TODO: Save this property ?
  }, [translates, langOrig, langTrans])

  const fixPageNumber = (p, s, count) => (p * s > count ? Math.ceil(count / s) : p)

  const refreshPage = (pageNumber, pageSize) => {
    setSize(pageSize)
    const fixedNumber = fixPageNumber(pageNumber, pageSize, translates.count)
    setPage(fixedNumber)
    transMarkList(id, fixedNumber, pageSize, same, noTrans)
  }
  const changeSame = () => {
    transMarkList(id, page, size, !same, noTrans)
    setSame(!same)
  }
  const changeNoTrans = () => {
    let val = noTrans > 0 ? 0 : langTrans
    transMarkList(id, page, size, same, val)
    setNoTrans(val)
  }

  return (
    <div className='explorer'>
      <TranslateMenu
        langOrig={langOrig}
        setLangOrig={setLangOrig}
        langTrans={langTrans}
        setLangTrans={setLangTrans}
        same={same}
        setSame={changeSame}
        noTrans={noTrans}
        setNoTrans={changeNoTrans}
      />
      <div className='explorer-scroll'>
        {translatesLoading ? (
          <Loader />
        ) : !translates.results ? (
          <div>NO ITEMS</div>
        ) : (
          translates.results.map((mark) => (
            <TranslateMark key={mark.id} mark={mark} langOrig={langOrig} langTrans={langTrans} same={same} />
          ))
        )}
      </div>
      <Paginator page={page} size={size} total={translates.count} refresh={refreshPage} />
    </div>
  )
}

export default PageTranslateFile
