import React, { useEffect, useContext, useState } from "react"
import { useParams } from "react-router-dom"
import AppContext from "../../context/application/appContext"
import TranslateMenu from "./TranslateMenu"
import TranslateMenu2 from "./TranslateMenu2"
import TranslateMark from "./TranslateMark"
import Paginator from "../AppComponents/Paginator"
import Loader from "../AppComponents/Loader"
import { IcoLang, IcoLangMap } from "../icons"
import { DisplayImage } from "../images"

const PageTranslateFile = (props) => {
  // STATE
  const { id } = useParams()
  const { transMarkList, transFileInfo, translates } = useContext(AppContext)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(25)
  const [same, setSame] = useState(false)
  const [noSame, setNoSame] = useState(false)
  const [like, setLike] = useState(false)
  const [noTrans, setNoTrans] = useState(0)
  const [langOrig, setLangOrig] = useState(null)
  const [langTrans, setLangTrans] = useState(null)

  useEffect(() => {
    transFileInfo(id, page, size, same, noTrans) // TODO: make like Promise
    // eslint-disable-next-line
  }, [id])

  useEffect(() => {
    if (!translates.lang_orig) return
    if (!langOrig) setLangOrig(translates.lang_orig)
    if (!langTrans && translates.translated_set.length) setLangTrans(translates.translated_set[0].language)
    setLoading(false)
  }, [translates, langOrig, langTrans])

  const fixPageNumber = (p, s, count) => (p * s > count ? Math.ceil(count / s) : p)

  const refreshPage = (pageNumber, pageSize) => {
    const fixedNumber = fixPageNumber(pageNumber, pageSize, translates.count)
    setLoading(true)
    setPage(fixedNumber)
    setSize(pageSize)
    transMarkList(id, fixedNumber, pageSize, same, noTrans).then(() => {
      setLoading(false)
    })
  }
  // const changeSame = () => {
  //   transMarkList(id, page, size, !same, noTrans)
  //   setSame(!same)
  // }
  const changeNoTrans = () => {
    let val = noTrans ? 0 : langTrans
    transMarkList(id, page, size, same, val)
    setNoTrans(val)
  }

  return (
    <div className='container-fluid'>
      {loading ? (
        <Loader />
      ) : (
        <>
          <div className='row justify bottom'>
            <div className='row center'>
              <div className='card card-image-small'>
                <DisplayImage name='extensions2' />
              </div>
              <h1 className='t-big ph-2'>{translates.name}</h1>
            </div>
            <div className='card p-1'>
              <div className='row center'>
                <div className='mh-2 col'>элементов</div>
                <div className='mh-2 col col-3'>{translates.items}</div>
              </div>
              <div className='row center mt-2'>
                <div className='mh-2 col'>слов</div>
                <div className='mh-2 col col-3'>{translates.words}</div>
              </div>
            </div>
          </div>
          <hr />
          <TranslateMenu2
            langOrig={langOrig}
            setLangOrig={setLangOrig}
            langTrans={langTrans}
            setLangTrans={setLangTrans}
            same={same}
            setSame={setSame}
            noSame={noSame}
            setNoSame={setNoSame}
            like={like}
            setLike={setLike}
            noTrans={noTrans}
            setNoTrans={changeNoTrans}
          />
          <div className='expl column'>
            <div className='scroll-y paginate'>
              {!translates.results ? (
                <div>NO ITEMS</div>
              ) : (
                translates.results.map((mark) => (
                  <TranslateMark key={mark.id} mark={mark} langOrig={langOrig} langTrans={langTrans} same={same} />
                ))
              )}
            </div>
            <Paginator page={page} size={size} total={translates.count} refresh={refreshPage} />
          </div>
        </>
      )}
    </div>
  )
}

export default PageTranslateFile
