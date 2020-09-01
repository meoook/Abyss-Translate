import React, { useContext, useState, useEffect } from "react"
import { useParams } from "react-router-dom"

import AppContext from "../../context/application/appContext"
import { IcoGet } from "../icons"

import ModalFolderCreate from "./ModalFolderCreate"
import ContentAriaProject from "./ContentAriaProject"
import ContentAriaFolder from "./ContentAriaFolder"
import OptionsFile from "./OptionsFile"
import OptionsFolder from "./OptionsFolder"
import OptionsProject from "./OptionsProject"

const ProjectError = ({ id, title, text }) => {
  return (
    <div className='container-fluid'>
      <h1>{title}</h1>
      <hr />
      <h3>
        {text}: {id}
      </h3>
    </div>
  )
}
// UTILS
// const rootFolder = (folderID, proj) => {
//   if (!proj || !proj.folders_set.length) return null
//   const searchFolders = proj.folders_set.filter((item) => item.id !== folderID)
//   const prj = searchFolders.find((folder) => folder.position === 1)
//   if (prj) return prj.id
//   return searchFolders.find((folder) => folder.position > 1).id
// }

//
export const PageExplorer = (props) => {
  // UTILS
  const getProj = (searchID, projs) => projs.find((prj) => prj.save_id === searchID)
  // STATE
  const { user, projects, explorer, languages, folderAdd, folderUpdate, folderRemove } = useContext(AppContext)
  const { id } = useParams()
  const [showModal, setShowModal] = useState(false)
  const [toggle, setToggle] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [project, setProject] = useState(getProj(id, projects))
  const [selectedFolder, setSelectedFolder] = useState(0)
  useEffect(() => {
    setSelectedFile(0)
    setSelectedFolder(0)
  }, [id])
  useEffect(() => {
    const prj = getProj(id, projects)
    console.log(id, projects)
    setProject(getProj(id, projects))
  }, [id, projects])
  // Handlers
  const folderAddByName = (name) => {
    folderAdd({ project: id, name }).then((folderID) => {
      setShowModal(false)
      setSelectedFolder(folderID)
    })
  }
  const folderRemoveUI = (folderID) => {
    setSelectedFolder(0)
    folderRemove(folderID, id)
  }
  const selectFolder = (folderID) => {
    setSelectedFolder(folderID)
    setSelectedFile(null)
  }
  // ERROR BLOCK
  // if (!project) return <ProjectError id={id} title={"Project not found"} text={"wrong project ID"} />
  // NORMAL BLOCK
  return (
    <>
      {!project || !project.name ? (
        <ProjectError id={id} title={"Project not found"} text={"wrong project ID"} />
      ) : (
        <div className={`explorer row${toggle && (explorer.count !== 0 || selectedFolder === 0) ? " wide" : ""}`}>
          <button className='slider-toggler' onClick={setToggle.bind(this, !toggle)}>
            <IcoGet name='arrows' />
          </button>
          {showModal && <ModalFolderCreate closeModal={setShowModal.bind(this, false)} folderAdd={folderAddByName} />}
          <div className='col col-2 column'>
            <div className='m-2'>
              <div className='mh-2 column'>
                <button className='btn green' onClick={setShowModal.bind(this, true)}>
                  Создать папку
                </button>
              </div>
              <hr />
              <div className='explorer-scroll column'>
                <button
                  className={`btn-f folder${!selectedFolder ? " selected" : ""}`}
                  onClick={selectFolder.bind(this, 0)}>
                  <i>
                    <IcoGet name='work' />
                  </i>
                  <span className='t-big'>. . .</span>
                </button>
                {project.folders_set
                  .sort((a, b) => a.position - b.position)
                  .map((folder) => (
                    <button
                      key={folder.id}
                      className={`btn-f folder${
                        selectedFolder === folder.id ? (selectedFile ? " active" : " selected") : ""
                      }`}
                      onClick={selectFolder.bind(this, folder.id)}
                      draggable={folder.position > 0}>
                      <i>
                        <IcoGet name='folder' />
                      </i>
                      <span>{folder.name}</span>
                    </button>
                  ))}
              </div>
              <div className='fix-bot column'>
                <hr />
                <div className='mh-2 column mb-0'>
                  <button className='btn blue'>Рандом кнопка</button>
                </div>
              </div>
            </div>
          </div>
          {!selectedFolder ? (
            <ContentAriaProject project={project} languages={languages} />
          ) : (
            <ContentAriaFolder
              selectFile={setSelectedFile}
              selectedFile={selectedFile}
              selectedFolder={selectedFolder}
            />
          )}
          <div className='explorer-slider'>
            {selectedFile ? (
              <OptionsFile id={selectedFile} fileList={explorer.results} />
            ) : selectedFolder ? (
              <OptionsFolder
                id={selectedFolder}
                project={project}
                fRemove={folderRemoveUI}
                fUpdate={folderUpdate}
                amount={explorer.count}
              />
            ) : (
              <OptionsProject project={project} />
            )}
          </div>
        </div>
      )}
    </>
  )
}
export default PageExplorer
