import React, { useContext, useState } from "react"
import AppContext from "../../../context/application/appContext"

import Dropzone from "../Dropzone"

export default function DropzoneFile({ folderID, fileID, langID }) {
  const { addMsg, uploadLangFile } = useContext(AppContext)
  const [uploadFile, setUploadFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [upProgress, setUpProgress] = useState(0)
  const [success, setSuccess] = useState(false)

  const setUpFile = (inFiles) => {
    if (inFiles.length === 0) return // If user press chancel after explorer window apear
    if (inFiles[0].type.substring(0, 4) !== "text" && inFiles[0].type !== "application/vnd.ms-excel") {
      addMsg({ text: inFiles[0].name, title: "File not text format", type: "error" })
      return false
    }
    if (uploadFile && inFiles[0].name === uploadFile.name) {
      addMsg({ text: inFiles[0].name, title: "File already in list", type: "warning" })
      return false
    }
    setUploadFile(inFiles[0])
    return true
  }

  const clearUploadedFiles = () => {
    setUploadFile(null)
    setUpProgress(0)
    setSuccess(false)
  }

  const goUploadFile = async () => {
    if (!folderID) return
    setUploading(true)
    await uploadLangFile(folderID, fileID, langID, uploadFile, setUpProgress)
      .then((res) => {
        setSuccess(true)
      })
      .catch((err) => {
        setSuccess(false)
      })
    setUploading(false)
  }

  return (
    <>
      <div className='sticky mt-2 ml-3'>
        <Dropzone addFiles={setUpFile} disabled={uploading || success} isSolo={true} />
        {uploadFile ? (
          <div className='row center justify m-2'>
            <div>&nbsp;</div>
            {success ? (
              <button className='btn green' onClick={clearUploadedFiles}>
                Очистить
              </button>
            ) : (
              <button className='btn blue' onClick={goUploadFile} disabled={uploading}>
                Загрузить файл
              </button>
            )}
          </div>
        ) : (
          <></>
        )}
      </div>
      {Boolean(uploadFile) && (
        <div className='scroll-y column ml-3'>
          <div className='input-group m-1'>
            <div className='input-like'>
              {uploadFile.name}
              <div className='input-progress t-right' style={{ width: upProgress + "%" }}></div>
            </div>
            {uploading ? (
              <div className='btn blue'>&gt;</div>
            ) : success ? (
              <div className='btn green'>v</div>
            ) : (
              <button className='btn red' onClick={() => setUploadFile(null)}>
                &times;
              </button>
            )}
          </div>
        </div>
      )}
    </>
  )
}
