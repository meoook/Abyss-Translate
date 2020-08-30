import React, { useContext, useEffect } from "react"
import { NavLink, Link } from "react-router-dom"
import Loader from "./Loader"
import AppContext from "../../context/application/appContext"
import { IcoGet } from "../icons"
import { textCutByLen } from "../componentUtils"
// THIS MODULE HAVE INCODE SVG

export const MenuMain = ({ closed, changeOpen }) => {
  const { languages, fetchLang, state, projects, prjList } = useContext(AppContext)

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
          &nbsp;
        </NavLink>
        {closed ? <hr /> : <div className='menu-title'>Меню</div>}
        <div>
          <NavLink to='/translates' className='menu-item'>
            <i>
              <svg xmlns='http://www.w3.org/2000/svg' height='24' width='24' viewBox='0 0 24 24'>
                <path d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zm6.93 6h-2.95c-.32-1.25-.78-2.45-1.38-3.56 1.84.63 3.37 1.91 4.33 3.56zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 1.32-.14 2 0 .68.06 1.34.14 2H4.26zm.82 2h2.95c.32 1.25.78 2.45 1.38 3.56-1.84-.63-3.37-1.9-4.33-3.56zm2.95-8H5.08c.96-1.66 2.49-2.93 4.33-3.56C8.81 5.55 8.35 6.75 8.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 1.43-1.08 2.76-1.91 3.96zM14.34 14H9.66c-.09-.66-.16-1.32-.16-2 0-.68.07-1.35.16-2h4.68c.09.65.16 1.32.16 2 0 .68-.07 1.34-.16 2zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95c-.96 1.65-2.49 2.93-4.33 3.56zM16.36 14c.08-.66.14-1.32.14-2 0-.68-.06-1.34-.14-2h3.38c.16.64.26 1.31.26 2s-.1 1.36-.26 2h-3.38z' />
              </svg>
            </i>
            <span>Перевод файлов</span>
          </NavLink>
          <NavLink to='/' exact className='menu-item'>
            <i>
              <svg xmlns='http://www.w3.org/2000/svg' height='24' width='24' viewBox='0 0 24 24'>
                <path d='M17,11V3H7v4H3v14h8v-4h2v4h8V11H17z M7,19H5v-2h2V19z M7,15H5v-2h2V15z M7,11H5V9h2V11z M11,15H9v-2h2V15z M11,11H9V9h2 V11z M11,7H9V5h2V7z M15,15h-2v-2h2V15z M15,11h-2V9h2V11z M15,7h-2V5h2V7z M19,19h-2v-2h2V19z M19,15h-2v-2h2V15z' />
              </svg>
            </i>
            <span>Мой профайл</span>
          </NavLink>
          {closed ? <hr /> : <div className='menu-title'>Ваши игры</div>}
        </div>
        <div className='menu-list mb-1'>
          {state.loading ? (
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
        <Link to='/prj/add' className='menu-add'>
          Add Game
        </Link>
        <hr />
        <button className={`menu-toggle${closed ? " rotated" : ""}`} onClick={toggleMenu}>
          <IcoGet name='arrows' />
        </button>
      </div>
    </div>
  )
}

export default MenuMain
