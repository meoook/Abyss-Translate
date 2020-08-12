import React, { useContext, useState } from "react"

import AppContext from "../../context/application/appContext"

import Dropzone from "./Dropzone"

export default function UploadFiles(props) {
  const { addMsg } = useContext(AppContext)
  const [uploadFiles, setUploadFiles] = useState([])

  const addUploadFiles = (inFiles) => {
    if (inFiles.length === 0) return // If user press chancel after explorer window apear
    const filtredFiles = inFiles.filter((inFile) => {
      if (inFile.type.substring(0, 4) !== "text" && inFile.type !== "application/vnd.ms-excel") {
        addMsg({ title: inFile.name, text: "File not text format", type: "error" })
        return false
      }
      for (let upFile of uploadFiles) {
        if (inFile.name === upFile.name && inFile.size === upFile.size && inFile.type === upFile.type) {
          addMsg({ title: inFile.name, text: "File already in list", type: "warning" })
          return false
        }
      }
      return true
    })
    setUploadFiles([...uploadFiles, ...filtredFiles])
  }

  // const removeUploadFile = (file) => {}

  return (
    <div>
      <h3>Загрузить файл</h3>
      <Dropzone addFiles={addUploadFiles} />
      <FileList files={uploadFiles} />
      <hr />
    </div>
  )
}

const FileList = ({ files }) => files.map((file, index) => <div key={index}>{file.name}</div>)
