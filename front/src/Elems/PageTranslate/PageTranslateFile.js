import React, { useEffect, useContext, useState } from "react"
import { useParams } from "react-router-dom"
import AppContext from "../../context/application/appContext"
import TranslateMenu from "./TranslateMenu"
import TranslateMark from "./TranslateMark"
import Paginator from "../AppComponents/Paginator"
import Loader from "../AppComponents/Loader"
import { DisplayImage } from "../images"
// import TranslateVariants from "./TranslateVariants"
import VariantGoogle from "./VarinatGoogle"
import VariantServer from "./VariantServer"
import MarkChangeLog from "./MarkChangeLog"

const getProgress = (count, totalCount) => `${Math.round((count / totalCount) * 100)}%`

const PageTranslateFile = (props) => {
  // STATE
  const { id } = useParams()
  const { transList, transFileInfo, translates } = useContext(AppContext)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(25)
  const [same, setSame] = useState(false)
  const [noSame, setNoSame] = useState(false)
  const [like, setLike] = useState(false)
  const [noTrans, setNoTrans] = useState(0)
  const [langOrig, setLangOrig] = useState(null)
  const [langTrans, setLangTrans] = useState(null)
  const [transProgress, setTransProgress] = useState(0)
  const [activeMark, setActiveMark] = useState(null)
  const [searchText, setSearchText] = useState("")

  useEffect(() => {
    if (id) transFileInfo(id, page, size, same, noTrans) // TODO: make like Promise
    // eslint-disable-next-line
  }, [id])

  useEffect(() => {
    if (!translates.lang_orig) return // translates not loaded
    if (!langOrig) setLangOrig(translates.lang_orig)
    if (!langTrans) setLangTrans(translates.translated_set[0].language)
    setLoading(false)
  }, [translates, langOrig, langTrans])

  useEffect(() => {
    if (langTrans) {
      const selectedTransObj = translates.translated_set.find((item) => item.language === langTrans)
      if (selectedTransObj) setTransProgress(getProgress(selectedTransObj.items, translates.items))
    } else setTransProgress(0)
  }, [langTrans])

  const fixPageNumber = (p, s, count) => (p * s > count ? Math.ceil(count / s) : p)

  const refreshPage = (pageNumber, pageSize) => {
    const fixedNumber = fixPageNumber(pageNumber, pageSize, translates.count)
    setLoading(true)
    setPage(fixedNumber)
    setSize(pageSize)
    transList(id, fixedNumber, pageSize, same, noTrans).then(() => {
      setLoading(false)
    })
  }
  const changeSearch = (searchText) => {
    transList(id, page, size, !noSame, noTrans, searchText)

    setSearchText(searchText)
  }
  const changeSame = () => {
    transList(id, page, size, !noSame, noTrans, searchText)
    setNoSame(!noSame)
  }
  const changeNoTrans = () => {
    let val = noTrans ? 0 : langTrans
    transList(id, page, size, same, val, searchText)
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
            searchText={searchText}
            setSearchText={changeSearch}
            langProgress={transProgress}
          />
          <div className='expl row'>
            <div className='col col-7 column'>
              <div className='table-head'>Текст для перевода</div>
              <div className={`scroll-y${translates.count / size > 1 ? " paginate" : ""}`}>
                {!translates.results || !translates.results.length ? (
                  <h3 className='m-2 mh-3'>&nbsp;Список пуст</h3>
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
                <span>Варианты перевода</span>
                <span className='color-error t-vsmall ml-1'>&nbsp;(в стадии разработки)</span>
              </div>
              <div className='scroll-y ml-3'>
                <VariantGoogle markID={activeMark} />
                <VariantServer markID={activeMark} />
                {Boolean(activeMark) && <MarkChangeLog mark={activeMark} fileID={id} />}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default PageTranslateFile
