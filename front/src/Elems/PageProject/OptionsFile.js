import React, { useState, useEffect } from "react"

import { displayStringDate } from "../componentUtils"
import InputCkeckField from "../AppComponents/InputCheckField"
import { IcoLangMap } from "../icons"
import FileTranslatedStatus from "../AppComponents/FileTranslatedStatus"

const OptionsFile = ({ id, fileList }) => {
  // TODO: Income file_obj
  const [selectedFile, setSelectedFile] = useState(fileList.find((item) => item.id === id))

  useEffect(() => {
    setSelectedFile(fileList.find((item) => item.id === id))
  }, [id, fileList])

  const saveName = (name) => {
    console.log(name)
    return false
    // fUpdate({
    //   project: project.save_id,
    //   id: id,
    //   name,
    //   repository,
    // })
  }

  // FIXME: No search ?!
  return (
    <>
      <div className='m-3'>
        <div className='mh-2 m-3'>
          <InputCkeckField value={selectedFile.name} setValue={saveName} ico='descr' big={true} />
        </div>
        <div className='mh-2 column center shadow-box'>
          <h2>Статус перевода</h2>
          <FileTranslatedStatus fileObj={selectedFile} />
        </div>
        <div className='explorer-scroll'>
          <table className='stats'>
            <tbody>
              <tr>
                <td>Состояние</td>
                <td>{selectedFile.state}</td>
              </tr>
              <tr>
                <td>Репозиторий</td>
                <td>{selectedFile.repository ? selectedFile.repository : "not set"}</td>
              </tr>
              <tr>
                {/* Состояние готовности % скачать */}
                <td>Необходим перевод</td>
                <td>
                  <IcoLangMap mapLanguages={selectedFile.translated_set.map(item => item.language)} />
                </td>
              </tr>
              <tr>
                <td>Слов в файле</td>
                <td>{selectedFile.words}</td>
              </tr>
              <tr>
                <td>Последнее изменение</td>
                <td>{displayStringDate(selectedFile.updated)}</td>
              </tr>
            </tbody>
          </table>
          <hr />
        </div>
        <div className='fix-bot column'>
          <hr />
          <div className='row center justify mh-2 mb-0'>
            <div>&nbsp;</div>
            <div>
              <button className='btn red'>Удалить файл (f)</button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default OptionsFile
