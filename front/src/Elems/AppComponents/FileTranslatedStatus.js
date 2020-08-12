import React, { useState, useEffect, useContext } from "react"
import { IcoLang } from "../icons"
import AppContext from "../../context/application/appContext"

const FileTranslatedStatus = ({ fileObj }) => {
  // UTILS
  const createFilename = (origName, langShortName) => {
    const nameSplited = origName.split(".")
    if (nameSplited.length > 1) {
      const extention = nameSplited.pop()
      return `${nameSplited.join()}-${langShortName}.${extention}`
    }
    return `${origName}-${langShortName}`
  }
  const getProgress = (count, totalCount) => `${Math.round((count / totalCount) * 100)}%`
  const findLang = (langID, languages) => languages.find((lang) => lang.id === langID)

  // STATE
  const { downloadFile, languages } = useContext(AppContext)
  const [translates, setTranslates] = useState(fileObj.translated_set)
  const [total, setTotal] = useState(fileObj.items_count)

  useEffect(() => {
    setTranslates(fileObj.translated_set)
    setTotal(fileObj.items_count)
  }, [fileObj])

  return (
    <div className='row'>
      {translates.map((item) => (
        <React.Fragment key={item.id}>
          {item.finished ? (
            <div
              onClick={downloadFile.bind(
                this,
                item.id,
                createFilename(fileObj.name, findLang(item.language, languages).short_name)
              )}
              className='pr-1'>
              <i className='bd'>
                <IcoLang language={findLang(item.language, languages).name} />
              </i>
              {findLang(item.language, languages).short_name} {getProgress(item.items_count, total)}
            </div>
          ) : (
            <div className='pr-1'>
              <i className='bd'>
                <IcoLang language={findLang(item.language, languages).name} />
              </i>
              {findLang(item.language, languages).short_name} {getProgress(item.items_count, total)}
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  )
}

export default FileTranslatedStatus
