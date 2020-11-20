import React, { useContext } from "react"
import AppContext from "../../context/application/appContext"
import { IcoGet } from "../icons"

const Header = (props) => {
  const { user, accLogout } = useContext(AppContext)
  const logOff = () => {
    accLogout()
  }

  return (
    <header className='row center justify'>
      <div>
        <h4 className='m-0'>Система переводов</h4>
        <div className='row center'>
          <i>
            <IcoGet name='language' />
          </i>
          <div>Профессиональный перевод игр</div>
        </div>
      </div>
      <div>
        <span className='mh-3'>{user.first_name}</span>
        <button className='btn red' onClick={logOff}>
          Выход
        </button>
      </div>
    </header>
  )
}

export default Header
