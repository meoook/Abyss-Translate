import React, { useContext, useEffect } from "react"
import { NavLink } from "react-router-dom"
import Loader from "./Loader"
import AppContext from "../../context/application/appContext"
import { IcoGet } from "../icons"
import { textCutByLen } from "../componentUtils"
// THIS MODULE HAVE INCODE SVG

export const MenuMain = ({ closed, changeOpen }) => {
  const { languages, fetchLang, loading, projects, prjList } = useContext(AppContext)

  useEffect(() => {
    if (!languages.length) fetchLang()
    prjList()
    // eslint-disable-next-line
  }, [])

  const toggleMenu = () => changeOpen(closed)

  return (
    <div className={`menu${closed ? " hide" : ""}`}>
      <div className='menu-container column'>
        <NavLink to='/ru' className='menu-logo'>
          <IcoGet name='logofull' />
        </NavLink>
        {closed ? <hr /> : <div className='menu-title'>Меню</div>}
        <div>
          <NavLink to='/translates' className='menu-item'>
            <i>
              <IcoGet name='language' />
            </i>
            <span>Перевод файлов</span>
          </NavLink>
          <NavLink to='/' exact className='menu-item'>
            <i>
              <IcoGet name='apartment' />
            </i>
            <span>Мой профайл</span>
          </NavLink>
          {closed ? <hr /> : <div className='menu-title'>Игры</div>}
        </div>
        <div className='menu-list mb-3'>
          {loading ? (
            <Loader />
          ) : (
            projects.map((prj) => (
              <NavLink to={`/prj/${prj.save_id}`} className='menu-item' key={prj.save_id}>
                <i>{prj.icon_chars}</i>
                <span>{textCutByLen(prj.name, 20)}</span>
              </NavLink>
            ))
          )}
        </div>
        <div className='fix-bot mb-1'>
          <hr />
          <button className={`menu-toggle${closed ? " rotated" : ""}`} onClick={toggleMenu}>
            <IcoGet name='arrows' />
          </button>
        </div>
      </div>
    </div>
  )
}

export default MenuMain
