import React, { useContext, useState, useEffect } from "react"

import AppContext from "../../context/application/appContext"

import Dropzone from "./Dropzone"

export default function DropzoneFileList({ folderID }) {
  const { addMsg, uploadFile } = useContext(AppContext)
  const [uploadFilesArr, setUploadFilesArr] = useState([])
  const [uploading, setUploading] = useState(false)
  const [upProgress, setUpProgress] = useState({}) // Can only catch for one file
  const [success, setSuccess] = useState(false)

  const addUploadFiles = (inFiles) => {
    if (inFiles.length === 0) return // If user press chancel after explorer window apear
    const filtredFiles = inFiles.filter((inFile) => {
      if (inFile.type.substring(0, 4) !== "text" && inFile.type !== "application/vnd.ms-excel") {
        addMsg({ text: inFile.name, title: "File not text format", type: "error" })
        return false
      }
      for (let upFile of uploadFilesArr) {
        if (inFile.name === upFile.name) {
          // && inFile.size === upFile.size && inFile.type === upFile.type) {
          addMsg({ text: inFile.name, title: "File already in list", type: "warning" })
          return false
        }
      }
      return true
    })
    setUploadFilesArr([...uploadFilesArr, ...filtredFiles])
  }
  const removeUploadFile = (file) => {
    setUploadFilesArr(uploadFilesArr.filter((item) => item !== file))
  }
  const clearUploadedFiles = () => {
    setUploadFilesArr([])
    setUpProgress({}) // It will refresh FileList
    setSuccess(false)
  }
  const uploadUploadFIles = async () => {
    if (!folderID) return
    setUploading(true)
    await uploadAllFiles(uploadFilesArr)
  }
  const uploadAllFiles = async (files) => {
    const count = files.length
    let check_count = 0
    files.forEach(async (file) => {
      // TODO: CallBacks for errors
      await uploadFile(folderID, file, setUpProgress)
        .then((res) => {
          check_count++
        })
        .catch((err) => {
          check_count++
        })
      if (count === check_count) {
        setSuccess(true)
        setUploading(false)
        // explList()
      }
    })
  }

  return (
    <>
      <div className='sticky mt-2 ml-3'>
        <Dropzone addFiles={addUploadFiles} disabled={uploading || success} />
        {uploadFilesArr.length ? (
          <div className='row center justify m-2'>
            <div>&nbsp;</div>
            {success ? (
              <button className='btn green' onClick={clearUploadedFiles}>
                Очистить
              </button>
            ) : (
              <button className='btn blue' onClick={uploadUploadFIles} disabled={uploading}>
                Загрузить файлы
              </button>
            )}
          </div>
        ) : (
          <></>
        )}
      </div>
      <div className='scroll-y column ml-3'>
        <FileList
          files={uploadFilesArr}
          removeFile={removeUploadFile}
          uploading={uploading}
          success={success}
          upProgress={upProgress}
        />
      </div>
    </>
  )
}

const FileList = ({ files, removeFile, uploading, success, upProgress }) => {
  const [allFilesProgress, setAllFilesProgress] = useState({})
  useEffect(() => {
    if (Object.keys(upProgress).length === 0) setAllFilesProgress({})
    else setAllFilesProgress({ ...allFilesProgress, ...upProgress })
    // eslint-disable-next-line
  }, [upProgress])

  const renderProgress = (file) => {
    const uploadProgress = allFilesProgress[file.name]
    if (uploading || success) return <Progress progress={uploadProgress ? uploadProgress : 0} />
    return <></>
  }

  return files.map((file) => (
    <div className='input-group m-1' key={file.name}>
      <div className='input-like'>
        {file.name}
        {renderProgress(file)}
      </div>
      {uploading ? (
        <div className='btn blue'>&gt;</div>
      ) : success ? (
        <div className='btn green'>v</div>
      ) : (
        <button className='btn red' onClick={removeFile.bind(this, file)}>
          &times;
        </button>
      )}
    </div>
  ))
}

const Progress = ({ progress }) => {
  return (
    <div className='input-progress t-right' style={{ width: progress + "%" }}>
      {/* {progress > 50 && `${progress}%`} */}
    </div>
  )
}
