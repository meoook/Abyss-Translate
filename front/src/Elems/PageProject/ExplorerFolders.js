import React, { useContext, useState, useEffect } from "react"
import AppContext from "../../context/application/appContext"
import { IcoGet } from "../icons"
import Loader from "../AppComponents/Loader"
import ModalFolderCreate from "./ModalFolderCreate"

// UTILS
const getHeadFolder = (folders) => {
  if (!folders || !folders.length) return null
  return folders.sort((a, b) => a.position - b.position)[0].id
}

const ExplorerFolders = ({ setOpt, fldrID, setFldrID, prjID }) => {
  const { folders, fldrList, fldrAdd } = useContext(AppContext)
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    setFldrID(getHeadFolder(folders))
    // eslint-disable-next-line
  }, [folders])

  useEffect(() => {
    setOpt(null)
    setFldrID(null)
    setLoading(true)
    fldrList(prjID).then(() => {
      setLoading(false)
    })
    // eslint-disable-next-line
  }, [prjID])

  const selectFolder = (folderID) => {
    setOpt(null)
    setFldrID(folderID)
  }
  // HANDLERS
  const folderAddByName = (name) => {
    name = name.trim()
    name &&
      fldrAdd({ save_id: prjID, name }).then((folderID) => {
        setShowModal(false)
        setOpt(null)
        setFldrID(folderID)
      })
  }

  return (
    <div className='col col-3 column'>
      {showModal && <ModalFolderCreate closeModal={setShowModal.bind(this, false)} folderAdd={folderAddByName} />}
      <div className='table-head row middle'>Папки</div>
      <button className='btn-try m-1 p-1 ph-2' onClick={setShowModal.bind(this, true)}>
        Создать папку
      </button>
      <div className='scroll-y column'>
        {loading ? (
          <Loader />
        ) : !folders.length ? (
          <NoFoldersInfo />
        ) : (
          folders
            .sort((a, b) => a.position - b.position)
            .map((folder) => (
              <div key={folder.id} draggable={true} className='column box-folder'>
                <button
                  onClick={selectFolder.bind(this, folder.id)}
                  className={`btn-f folder m-0${fldrID === folder.id ? " selected" : ""}`}>
                  <i>
                    <IcoGet name='folder' />
                  </i>
                  <span>{folder.name}</span>
                </button>
                <button className='folder-options' onClick={setOpt.bind(this, folder.id)}>
                  <div>
                    <i>
                      <IcoGet name='settings' />
                    </i>
                    <div className='t-vsmall mt-0'>файлов {folder.files_amount}</div>
                  </div>
                </button>
              </div>
            ))
        )}
      </div>
    </div>
  )
}

export default ExplorerFolders

const NoFoldersInfo = (perms) => {
  return (
    <div className='card card-info'>
      <div className='card-info-attantion'>
        <IcoGet name='attantion' />
      </div>
      <h4>У вас нет ни одной папки</h4>
      <div>
        Нажмите на кнопку <b>"Создать папку"</b> для добавления
      </div>
      <div>Папки нужны чтоб добавлять в них файлы</div>
    </div>
  )
}
