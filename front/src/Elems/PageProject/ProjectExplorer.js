import React, { useState, useEffect } from "react"
import ExplorerFolders from "./ExplorerFolders"
import OptionsFolder from "./OptionsFolder"
import OptionsFile from "./File/OptionsFile"
import FileListByAccess from "./FileListByAccess"

const ProjectExplorer = ({ projectID, readOnly }) => {
  // Manage access
  const [optionsID, setOptionsID] = useState(null) // null for file list, folder_id for folder options display
  const [fldrID, setFldrID] = useState(null)
  const [fileID, setFileID] = useState(null) // to display file options

  useEffect(() => {
    setOptionsID(null)
  }, [projectID, readOnly])

  useEffect(() => {
    setFileID(null)
  }, [optionsID])

  const folderSelected = (fID) => {
    setFldrID(fID)
    setOptionsID(null)
    setFileID(null)
  }

  return (
    <div className='expl row mt-2'>
      {!readOnly && (
        <ExplorerFolders setOpt={setOptionsID} prjID={projectID} fldrID={fldrID} setFldrID={folderSelected} />
      )}
      {optionsID ? (
        <OptionsFolder fID={optionsID} prjID={projectID} />
      ) : fileID ? (
        <OptionsFile folderID={fldrID} fileID={fileID} />
      ) : (
        <FileListByAccess trOnly={readOnly} fldrID={fldrID} prjID={projectID} onOptClick={setFileID} />
      )}
    </div>
  )
}

export default ProjectExplorer
