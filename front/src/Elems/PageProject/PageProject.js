import React, { useContext, useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import AppContext from "../../context/application/appContext"
import { IcoLang, IcoLangMap } from "../icons"
import { DisplayImage } from "../images"
import ProjectExplorer from "./ProjectExplorer"
import Loader from "../AppComponents/Loader"
import OptionsProject from "./OptionsProject"
import ProjectPermissions from "./ProjectPermissions"

const ProjectError = ({ id }) => {
  return (
    <div className='container-fluid'>
      <h1>"Project not found"</h1>
      <hr />
      <h3>wrong project ID: {id}</h3>
    </div>
  )
}

export const PageProject = (props) => {
  // UTILS
  const getProj = (searchID, projs) => projs.find((prj) => prj.save_id === searchID)
  const getPerms = (prj, usr) => (prj.author === usr.first_name ? [0, 5, 8, 9, 99] : prj.permissions_set) // 99 - owner permission
  const hasPerm = (lookupPerms, userPerms) => Number.isInteger(lookupPerms.find((item) => userPerms.includes(item)))
  const translateOnly = (userPerms) => userPerms.length === 1 && userPerms[0] === 0
  // STATE
  const { user, projects, loading, languages } = useContext(AppContext)
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [permissions, setPermissions] = useState([])
  const [menuSelected, setMenuSelected] = useState("blank")
  const [trOnly, setTrOnly] = useState(false)

  useEffect(() => {
    const prj = getProj(id, projects)
    if (prj) {
      setProject(prj)
      const perms = getPerms(prj, user)
      setPermissions(perms)
      setTrOnly(translateOnly(perms))
      // TODO: menu selected
      if (menuSelected === "blank") {
        if (hasPerm([0, 8], perms)) {
          setMenuSelected("files")
        } else if (hasPerm([5, 9], perms)) {
          setMenuSelected("access")
        } else {
          setMenuSelected("warning")
        }
      }
    }
    // eslint-disable-next-line
  }, [id, projects, user]) // TODO: removed projects from here (have a bug but...)

  return (
    <>
      {loading || !languages.length ? (
        <Loader />
      ) : !project || !project.name || menuSelected === "warning" ? (
        <ProjectError id={id} />
      ) : (
        <div className='container-fluid'>
          <div className='row justify center'>
            <div className='row center'>
              <div className='card card-image-small mb-1'>
                <DisplayImage name={project.name.toLowerCase()} />
              </div>
              <h1 className='t-big ph-2'>{project.name}</h1>
            </div>
            <div className='card p-1 mb-1 pr-1'>
              <div className='row center'>
                <div className='mh-2'>Язык оригиналов</div>
                <IcoLang language={project.lang_orig} displayShort={true} />
              </div>
              <div className='row center mt-1'>
                <div className='mh-2'>Языки для перевода</div>
                <IcoLangMap mapLanguages={project.translate_to} />
              </div>
            </div>
          </div>
          <hr />
          {!trOnly && (
            <div className='box box-inline'>
              <div className='menu-inline'>
                {hasPerm([0, 8], permissions) && (
                  <button
                    className={`underline${menuSelected === "files" ? " active" : ""}`}
                    onClick={setMenuSelected.bind(this, "files")}>
                    Управление файлами
                  </button>
                )}
                {hasPerm([5, 9], permissions) && (
                  <button
                    className={`underline ${menuSelected === "access" ? " active" : ""}`}
                    onClick={setMenuSelected.bind(this, "access")}>
                    Управление доступом
                  </button>
                )}
                {hasPerm([99], permissions) && (
                  <button
                    className={`underline${menuSelected === "owner" ? " active" : ""}`}
                    onClick={setMenuSelected.bind(this, "owner")}>
                    Настройки игры
                  </button>
                )}
              </div>
            </div>
          )}
          {menuSelected === "blank" && <Loader />}
          {menuSelected === "files" && <ProjectExplorer projectID={id} readOnly={!permissions.includes(8)} />}
          {menuSelected === "access" && <ProjectPermissions prjID={id} />}
          {menuSelected === "owner" && <OptionsProject prjObj={project} />}
        </div>
      )}
    </>
  )
}
export default PageProject
