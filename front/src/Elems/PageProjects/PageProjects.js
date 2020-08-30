import React, { useContext } from "react"

import AppContext from "../../context/application/appContext"
import { IcoGet } from "../icons"
import ProjectElem from "./ProjectElem"

// HOME PAGE
export const PageProjects = (props) => {
  // STATE
  const { user, projects } = useContext(AppContext)

  return (
    <div className='container-fluid'>
      <h1>Your projects</h1>
      <hr />
      {projects.map((prj) => (
        <ProjectElem key={prj.save_id} project={prj} />
      ))}
    </div>
  )
}
export default PageProjects
