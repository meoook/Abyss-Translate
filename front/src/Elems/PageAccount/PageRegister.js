import React, { useState, useContext } from "react"
import PropTypes from "prop-types"
import { Redirect } from "react-router-dom"
import AppContext from "../../context/application/appContext"

// TODO: COMPONENT AND REDUCER NOT DONE

const PageRegister = (props) => {
  const { user, accRegister } = useContext(AppContext)
  const [credentials, setCredentials] = useState({ username: "", password: "", email: "" })
  const onChange = (event) => setCredentials({ ...credentials, [event.target.name]: event.target.value })
  const onRegister = (event) => {
    accRegister(credentials)
    // console.log("Register", credentials)
    // console.log("Register", credentials)
    // console.log("Register", credentials)
  }
  if (user.id) return <Redirect to={"/"} />

  return (
    <div className='column center middle max-h'>
      <div className='shadow-box col col-3'>
        <h1>Регистрация</h1>
        <label>Укажите ваш логин</label>
        <input name='username' type='text' onChange={onChange} />
        <label>Укажите почту</label>
        <input name='email' type='email' onChange={onChange} />
        <label>Укажите пароль</label>
        <input name='password' type='password' onChange={onChange} />
        <div className='row center justify'>
          <div>&nbsp;</div>
          <button className='btn green' onClick={onRegister}>
            Register
          </button>
        </div>
      </div>
    </div>
  )
}

PageRegister.propTypes = { auth: PropTypes.object }

export default PageRegister
