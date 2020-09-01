import React, { useContext, useState, useEffect } from "react"
import AppContext from "../../context/application/appContext"
import ExplorerFolders from "./ExplorerFolders"
import OptionsFolder from "./OptionsFolder"
import FileListByAccess from "./FileListByAccess"

const ProjectExplorer = ({ projectID, trOnly }) => {
  // Manage access
  const [optionsID, setOptionsID] = useState(null) // null for file list, folder_id for folder options display
  const [fldrID, setFldrID] = useState(null)

  useEffect(() => {
    setOptionsID(null)
  }, [projectID, trOnly])

  return (
    <div className='expl row mt-2'>
      {!trOnly && <ExplorerFolders setOpt={setOptionsID} prjID={projectID} fldrID={fldrID} setFldrID={setFldrID} />}
      {optionsID ? (
        <OptionsFolder fID={optionsID} prjID={projectID} />
      ) : (
        <FileListByAccess trOnly={trOnly} fldrID={fldrID} prjID={projectID} />
      )}
    </div>
  )
}

export default ProjectExplorer
