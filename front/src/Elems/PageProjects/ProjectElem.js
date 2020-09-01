import React from "react"
import { NavLink } from "react-router-dom"

import { IcoLangMap, IcoLang } from "../icons"
import { displayStringDate } from "../componentUtils"

export const ProjectElem = ({ project }) => {
  return (
    <NavLink to={`/prj/${project.save_id}`} className='table-line link big row center m-1'>
      <div className='col col-3'>
        <i className='big'>{project.icon_chars}</i>
        {project.name}
      </div>
      <div className='col col-2'>{project.author}</div>
      <div className='col col-2'>
        <IcoLang language={project.lang_orig} displayShort={true} />
      </div>
      <div className='col col-3'>
        <IcoLangMap mapLanguages={project.translate_to} />
      </div>
      <div className='col col-2'>{displayStringDate(project.created)}</div>
    </NavLink>
  )
}
export default ProjectElem
