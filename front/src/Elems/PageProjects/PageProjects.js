import React, { useContext } from "react"

import AppContext from "../../context/application/appContext"
import ProjectElem from "./ProjectElem"
import { Link } from "react-router-dom"

export const PageProjects = (props) => {
  const { user, projects } = useContext(AppContext)

  return (
    <div className='container-fluid p-2'>
      <div className='row bottom justify'>
        <h1>Игры</h1>

        {user.role === "creator" && (
          <Link to={`/prj/add`} className='btn green'>
            Добавить
          </Link>
        )}
      </div>
      <hr />
      <div className='table-head'>
        <div className='col col-3'>Название</div>
        <div className='col col-2'>Владелец</div>
        <div className='col col-2'>Язык оригиналов</div>
        <div className='col col-3'>Необходимые переводы</div>
        <div className='col col-2'>Дата создания</div>
      </div>
      {projects.map((prj) => (
        <ProjectElem key={prj.save_id} project={prj} />
      ))}
    </div>
  )
}
export default PageProjects
