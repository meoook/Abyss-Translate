import React, { useEffect, useContext, useState } from "react"
import AppContext from "../../context/application/appContext"
import { IcoGet } from "../icons"
import Loader from "../AppComponents/Loader"
import Paginator from "../AppComponents/Paginator"
import FileTranslatedStatus from "../AppComponents/FileTranslatedStatus"
import { Link } from "react-router-dom"
import { textCutByLen } from "../componentUtils"

const FileListByAccess = ({ trOnly, fldrID, prjID }) => {
  const [loading, setLoading] = useState(true)
  const { explorer, explList } = useContext(AppContext)
  const [fileList, setFileList] = useState([])
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(25)

  useEffect(() => {
    setLoading(true)
    if (trOnly) {
      explList(prjID, null, page, size)
    } else if (fldrID) {
      explList(prjID, fldrID, page, size)
    } else {
      explList(null, null)
    }
    // eslint-disable-next-line
  }, [fldrID, page, size])

  useEffect(() => {
    if (explorer.results) {
      setFileList(explorer.results)
    } else {
      setFileList([])
    }
    setLoading(false)
  }, [explorer])

  const refreshPage = (pageNumber, pageSize) => {
    setLoading(true)
    setPage(pageNumber)
    setSize(pageSize)
    if (trOnly)
      explList(prjID, null, page, size).then(() => {
        setLoading(false)
      })
    else if (fldrID) {
      explList(prjID, fldrID, pageNumber, pageSize).then(() => {
        setLoading(false)
      })
    }
  }

  return (
    <div className={`col col-${trOnly ? 12 : 9}`}>
      <div className={`table-head${!trOnly ? " ml-3" : ""}`}>
        <div className='col col-3'>Название</div>
        <div className='col col-2'>Позиций</div>
        <div className='col col-2'>Слов</div>
        <div className='col col-3'>Прогресс перевода</div>
        <div className='col col-2'>GIT статус</div>
      </div>
      <div className={`scroll-y paginate column m-1${!trOnly ? " ml-3" : ""}`}>
        {loading ? (
          <Loader />
        ) : !fileList.length ? (
          <div className='col col-4'>{trOnly ? <NoFilesList /> : fldrID ? <NoFilesInfo /> : <></>}</div>
        ) : (
          <>
            {fileList.map((item) => (
              <FileItem file={item} key={item.id} />
            ))}
            <Paginator page={page} size={size} total={explorer.count} refresh={refreshPage} />
          </>
        )}
      </div>
    </div>
  )
}

export default FileListByAccess

const NoFilesInfo = (perms) => {
  return (
    <div className='card card-info right'>
      <div className='card-info-attantion'>
        <IcoGet name='attantion' />
      </div>
      <h4>В папке нет ни одного файла</h4>
      <div>
        Нажмите на кнопку <b>"настройки папки"</b>&nbsp;
        <IcoGet name='settings' /> для перехода в меню добавления файлов
      </div>
      <div>В "настройках папки" так же можно поменять название папки и указать гит репозиторий</div>
    </div>
  )
}

const NoFilesList = (perms) => {
  return (
    <div className='card card-info'>
      <div className='card-info-attantion'>
        <IcoGet name='attantion' />
      </div>
      <h4>Список файлов пуст</h4>
      <div>Владелец игры должен загрузить файлы, после чего они будут отображаться в списке</div>
    </div>
  )
}
const FileItem = ({ file }) => {
  return (
    <div className='table-line m-0'>
      <div className='col col-3'>
        {file.state === "uploaded" || file.state === "error" ? (
          file.name
        ) : (
          <Link to={`/translates/${file.id}`}>
            <span>{textCutByLen(file.name, 25)}</span>
          </Link>
        )}
      </div>
      {file.state === "uploaded" ? (
        <div className='col col-8 row center'>
          <div>в обработке</div>
          <div className='loader-dots'>...</div>
        </div>
      ) : file.state === "error" ? (
        <div className='col col-8 row center'>
          <div className='color-error'>ошибка обработка файла</div>
        </div>
      ) : (
        <>
          <div className='col col-2'>{file.items}</div>
          <div className='col col-2'>{file.words}</div>
          <div className='col col-4'>
            <FileTranslatedStatus fileObj={file} />
          </div>
        </>
      )}
      <div className='col col-1'>{file.repo_status ? "Ok" : "X"}</div>
    </div>
  )
}
