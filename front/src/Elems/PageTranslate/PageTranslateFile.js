import React, { useEffect, useContext, useState } from "react"
import { useParams } from "react-router-dom"
import AppContext from "../../context/application/appContext"
import TranslateMenu from "./TranslateMenu"
import TranslateMark from "./TranslateMark2"
import Paginator from "../AppComponents/Paginator"
import Loader from "../AppComponents/Loader"
import { DisplayImage } from "../images"
// import TranslateVariants from "./TranslateVariants"
import VariantGoogle from "./VarinatGoogle"
import VariantServer from "./VariantServer"

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
  const [activeMark, setActiveMark] = useState(null)

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
  const changeSame = () => {
    transMarkList(id, page, size, !noSame, noTrans)
    setNoSame(!noSame)
  }
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
          <TranslateMenu
            langOrig={langOrig}
            setLangOrig={setLangOrig}
            langTrans={langTrans}
            setLangTrans={setLangTrans}
            same={same}
            setSame={setSame}
            noSame={noSame}
            setNoSame={changeSame}
            like={like}
            setLike={setLike}
            noTrans={noTrans}
            setNoTrans={changeNoTrans}
          />
          <div className='expl row'>
            <div className='col col-7 column'>
              <div className='table-head'>Текст для перевода</div>
              <div className={`scroll-y${translates.count / size > 1 ? " paginate" : ""}`}>
                <TranslateMark
                  key={1}
                  mark={{
                    translates_set: [
                      { id: 1, text: "text", language: 15 },
                      { id: 2, text: "text2", language: 18 },
                      { id: 3, text: "text3", language: 22 },
                      { id: 4, text: "text4", language: 75 },
                    ],
                    words: 16,
                    id: 2,
                  }}
                  langOrig={22}
                  langTrans={18}
                  same={same}
                  setActive={setActiveMark}
                />
                <TranslateMark
                  key={2}
                  mark={{
                    translates_set: [
                      { id: 5, text: "text5", language: 15 },
                      { id: 6, text: "text6", language: 18 },
                      { id: 7, text: "text7", language: 22 },
                      { id: 8, text: "text8", language: 75 },
                    ],
                    words: 5,
                    id: 1,
                  }}
                  langOrig={15}
                  langTrans={18}
                  same={same}
                  setActive={setActiveMark}
                />
                {!translates.results ? (
                  <div>NO ITEMS</div>
                ) : (
                  translates.results.map((mark) => (
                    <TranslateMark
                      key={mark.id}
                      mark={mark}
                      langOrig={langOrig}
                      langTrans={langTrans}
                      same={same}
                      setActive={setActiveMark}
                    />
                  ))
                )}
              </div>
              {translates.count / size > 1 && (
                <Paginator page={page} size={size} total={translates.count} refresh={refreshPage} />
              )}
            </div>
            <div className='col col-5 column'>
              <div className='table-head ml-3'>
                <div>Варианты перевода</div>
                <div className='color-error ml-2'>(в стадии разработки)</div>
              </div>
              <div className='scroll-y ml-3'>
                <VariantGoogle markID={activeMark} />
                <VariantServer markID={activeMark} />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default PageTranslateFile
