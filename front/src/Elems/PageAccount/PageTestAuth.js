import React from "react"
import { NavLink } from "react-router-dom"

const PageTestAuth = (props) => {
  const handleRedirect = () => {
    return props.history.push("/")
  }

  return (
    <div className='column center middle max-h'>
      <div className='shadow-box col col-3'>
        <h1>Redirect&nbsp;to&nbsp;Abyss&nbsp;page</h1>
        <div className='row center justify m-2'>
          <NavLink
            to={
              "/auth/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            }
            className='underline'>
            Link as in abyss to auth here
          </NavLink>
        </div>
        <div>
          <button className='btn green' onClick={handleRedirect}>
            Abyss
          </button>
        </div>
      </div>
    </div>
  )
}

export default PageTestAuth
