import React, { useState, useEffect } from "react"

import DropzoneFileList from "./DropzoneFileList"
import InputCkeckField from "../AppComponents/InputCheckField"

const OptionsFolder = ({ id, project, amount, fUpdate, fRemove }) => {
  // UTILS
  const findFolder = (fID, folders) => folders.find((item) => item.id === fID)

  // STATE
  const [folder, setFolder] = useState(findFolder(id, project.folders_set))
  const [repository, setRepository] = useState("")
  const [search, setSearch] = useState([]) // User folders name list to filter when input

  useEffect(() => {
    const fld = findFolder(id, project.folders_set)
    setFolder(fld)
    fld.repository ? setRepository(fld.repository) : setRepository("")
    setSearch(
      project.folders_set.reduce((res, item) => {
        if (item.id === fld.id) return res
        else return [...res, { name: item.name }] // Need only name here
      }, [])
    )
  }, [id, project])

  // Handlers
  const changeGit = (event) => {
    setRepository(event.target.value.trim())
  }
  const saveName = (name) => {
    fUpdate({
      project: project.save_id,
      id: id,
      name,
      repository,
    })
  }
  const saveGit = () => {
    fUpdate({
      project: project.save_id,
      id: id,
      name: folder.name,
      repository,
    })
  }
  return (
    <>
      <div className='m-3'>
        <div className='mh-2 m-3'>
          <InputCkeckField value={folder.name} setValue={saveName} ico='foldero' big={true} search={search} />
        </div>
        <div className='explorer-scroll'>
          <div className='mh-2'>
            <label>Сылка на папку в GIT репозитории (? что как)</label>
            <div>
              <input type='text' value={repository} onChange={changeGit} placeholder='не указано' onBlur={saveGit} />
            </div>
          </div>
          <table className='stats'>
            <tbody>
              <tr>
                <td>Всего файлов</td>
                <td>{amount}</td>
              </tr>
              <tr>
                <td>Файлы без переводов</td>
                <td>2 (f)</td>
              </tr>
            </tbody>
          </table>
          <DropzoneFileList folderID={id} />
        </div>
        <div className='fix-bot column'>
          <hr />
          <div className='row center justify mh-2 mb-0'>
            <div>&nbsp;</div>
            <div>
              <button className='btn red' onClick={fRemove.bind(this, id)}>
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
