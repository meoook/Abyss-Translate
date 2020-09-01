import React, { useState, useContext, useEffect } from "react"
import { Link } from "react-router-dom"

import AppContext from "../../context/application/appContext"

import { IcoGet } from "../icons"
import Loader from "../AppComponents/Loader"
import { textCutByLen } from "../componentUtils"

import Paginator from "../AppComponents/Paginator"
import ContentFolderStart from "./ContentFolderStart"
import FileTranslatedStatus from "../AppComponents/FileTranslatedStatus"

const ContentAriaFolder = ({ selectFile, selectedFile, selectedFolder }) => {
  const { explorer, explorerLoading, explorerList } = useContext(AppContext)
  const [fileList, setFileList] = useState([])
  // eslint-disable-next-line
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(25)
  useEffect(() => {
    explorerList(selectedFolder, page, size)
    // eslint-disable-next-line
  }, [selectedFolder, page, size])
  useEffect(() => {
    if (explorer.results) setFileList(explorer.results)
  }, [explorer])
  const refreshPage = (pageNumber, pageSize) => {
    setPage(pageNumber)
    setSize(pageSize)
    explorerList(selectedFolder, pageNumber, pageSize)
  }

  return (
    <div className='col col-10'>
      <div className='m-2 mh-2'>
        <div className='row center'>
          <div className='col col-1'>
            <i className='big'>
              <IcoGet name='search' />
            </i>
          </div>
          <div className='col col-2'>Имя</div>
          <div className='col col-2'>Состояние</div>
          <div className='col col-1 t-center'>Позиций</div>
          <div className='col col-1 t-center'>Cлов</div>
          <div className='col col-5'>Выполнены переводы</div>
        </div>
        <hr />
      </div>
      {explorerLoading ? (
        <Loader />
      ) : !fileList.length ? (
        <ContentFolderStart />
      ) : (
        <div className='explorer-scroll explorer-zebra'>
          {fileList.map((item) => (
            <FileItem file={item} key={item.id} selected={selectedFile} selectFile={selectFile} />
          ))}
        </div>
      )}
      <Paginator page={page} size={size} total={explorer.count} refresh={refreshPage} />
    </div>
  )
}

export default ContentAriaFolder

const FileItem = ({ file, selected, selectFile }) => {
  return (
    <div
      className={`btn-f${selected === file.id ? " selected" : ""} row center`}
      onClick={selectFile.bind(this, file.id)}>
      <div className='col col-3 row'>
        <div className='mh-1'>
          <input type='checkbox' />
        </div>
        {file.state === "uploaded" || file.state === "parse error" ? (
          <div>{file.name}</div>
        ) : (
          <Link to={`/translates/${file.id}`}>
            <span>{textCutByLen(file.name, 25)}</span>
          </Link>
        )}
      </div>
      <div className='col col-2'>{file.state}</div>
      <div className='col col-1 t-center'>{file.items}</div>
      <div className='col col-1 t-center'>{file.words}</div>
      <div className='col col-5 pt-0'>
        <FileTranslatedStatus fileObj={file} />
      </div>
    </div>
  )
}
