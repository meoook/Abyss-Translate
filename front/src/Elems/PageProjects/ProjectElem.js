import React from "react"

export const ProjectElem = ({ project }) => {
  return (
    <div className='row'>
      <div>{project.save_id}</div>
      <div>{project.name}</div>
      <div>{project.lang_orig}</div>
      <div>{project.translate_to}</div>
    </div>
  )
}
export default ProjectElem
