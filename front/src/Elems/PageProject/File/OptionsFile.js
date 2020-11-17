import React, { useState, useEffect, useContext } from "react"

import InputCkeckField from "../../AppComponents/InputCheckField"
import AppContext from "../../../context/application/appContext"
import FileTranslatedStatus from "../../AppComponents/FileTranslatedStatus"
import LanguageSelector from "../../AppComponents/LanguageSelector"
import DropzoneFile from "./DropzoneFile"

const OptionsFile = ({ folderID, fileID }) => {
  const { explorer, fileRemove, fileUpdate } = useContext(AppContext)
  // UTILS
  const findFile = (filoID, filesArr) => filesArr.find((item) => item.id === filoID)

  // STATE
  const [filo, setFilo] = useState(null)
  const [uploadLang, setUploadLang] = useState(null) // User file names list to filter\error when input

  useEffect(() => {
    const found = findFile(fileID, explorer.results)
    setFilo(found)
    if (found) setUploadLang(found.lang_orig)
  }, [fileID, explorer])

  const handleChangeName = (value) => {
    fileUpdate({ ...filo, name: value })
  }
  // Check file or no component
  if (!filo) return null

  return (
    <>
      <div className='col col-4 column'>
        <div className='table-head ml-3'>Загрузить переводы к файлу</div>
        <div className='mt-1 ml-3'>
          <LanguageSelector
            selected={uploadLang}
            setSelected={setUploadLang}
            langArr={[filo.lang_orig, ...filo.translated_set.map((itm) => itm.language)]}
          />
        </div>
        <div className='mt-1 ml-3'>Выберете язык переводов для загружаемого файла.</div>
        <div className='ml-3'>
          Если выбранный язык совпадает с языком оригиналов для файла, то переводы будут "пересобраны" с загружаемого
          файла
        </div>
        <DropzoneFile folderID={folderID} fileID={filo.id} langID={uploadLang} />
      </div>

      <div className='col col-5 column'>
        <div className='table-head ml-3'>
          <div>Настройки для файла</div>
        </div>

        <div className='m-3 ml-3'>
          <InputCkeckField value={filo.name} setValue={handleChangeName} ico='foldero' big={true} search={[]} />
        </div>

        {filo.translated_set.length > 0 && (
          <div className='ml-3'>
            <div>Прогресс перевода файла</div>
            <FileTranslatedStatus fileObj={filo} />
          </div>
        )}
        {Boolean(filo.error) && (
          <div className='ml-3 color-error'>
            <div>Невозможно обработать файл</div>
            <div>{filo.error}</div>
          </div>
        )}
        {Boolean(filo.warning) && (
          <div className='ml-3 color-warning'>
            <div>Возможные ошибки</div>
            <div>{filo.warning}</div>
          </div>
        )}

        <div className='fix-bot column ml-3'>
          <hr />
          <div className='row center justify'>
            <div>&nbsp;</div>
            <div>
              <button className='btn red' onClick={fileRemove.bind(this, filo.id)}>
                Удалить файл
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default OptionsFile
