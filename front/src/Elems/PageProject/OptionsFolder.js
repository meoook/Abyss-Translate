import React, { useState, useEffect, useContext } from "react"

import DropzoneFileList from "./DropzoneFileList"
import InputCkeckField from "../AppComponents/InputCheckField"
import AppContext from "../../context/application/appContext"

const OptionsFolder = ({ fID, prjID }) => {
  const { folders, fldrUpdate, fldrRemove } = useContext(AppContext)
  // UTILS
  const findFolder = (folderID, foldersArr) => foldersArr.find((item) => item.id === folderID)

  // STATE
  const [folder, setFolder] = useState(findFolder(fID, folders))
  const [repo, setRepo] = useState("")
  const [search, setSearch] = useState([]) // User folders name list to filter\error when input

  useEffect(() => {
    const fld = findFolder(fID, folders)
    if (fld) {
      setFolder(fld)
      fld.repo_url ? setRepo(fld.repo_url) : setRepo("")
      setSearch(
        folders.reduce((res, item) => {
          if (item.id === fld.id) return res
          else return [...res, { name: item.name }] // Need only name here
        }, [])
      )
    }
  }, [fID, folders, prjID])

  // Handlers
  const changeGit = (event) => {
    setRepo(event.target.value.trim())
  }
  const saveName = (name) => {
    if (name !== folder.name) fldrUpdate({ save_id: prjID, id: fID, name, repo_url: repo })
  }
  const saveGit = () => {
    if (repo !== folder.repo_url) fldrUpdate({ save_id: prjID, id: fID, name: folder.name, repo_url: repo })
  }
  return (
    <>
      <div className='col col-4 column'>
        <div className='table-head ml-3'>Загрузка файлов в папку</div>
        <DropzoneFileList folderID={fID} />
      </div>

      <div className='col col-5 column'>
        <div className='table-head ml-3'>
          <div>Настройки для папки</div>
        </div>

        <div className='m-3 ml-3'>
          <InputCkeckField value={folder.name} setValue={saveName} ico='foldero' big={true} search={search} />
        </div>

        <div className='scroll-y paginate column ml-3'>
          <label>Сылка на папку в GIT репозитории (?)</label>
          <div>
            <input type='text' value={repo} onChange={changeGit} placeholder='не указано' onBlur={saveGit} />
          </div>
        </div>

        <div className='fix-bot column ml-3'>
          <hr />
          <div className='row center justify'>
            <div>&nbsp;</div>
            <div>
              <button className='btn red' onClick={fldrRemove.bind(this, fID)}>
                Удалить папку
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default OptionsFolder
