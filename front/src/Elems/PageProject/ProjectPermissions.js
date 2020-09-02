import React from "react"

const ProjectPermissions = (props) => {
  return (
    <div className='expl row mt-2'>
      <div className='col col-6 column'>
        <div className='table-head'>
          <span>Список прав пользователей</span>
          <span className='color-error t-vsmall ml-1'>&nbsp;(в стадии разработки)</span>
        </div>
      </div>
      <div className='col col-6 column'>
        <div className='table-head ml-2'>
          <span>Выдача прав пользователям</span>
          <span className='color-error t-vsmall ml-1'>&nbsp;(в стадии разработки)</span>
        </div>
      </div>
    </div>
  )
}

export default ProjectPermissions
