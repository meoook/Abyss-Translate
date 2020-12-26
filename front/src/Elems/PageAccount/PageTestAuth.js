import React from 'react'
import { NavLink } from 'react-router-dom'

const PageTestAuth = (props) => {
  const handleRedirect = () => {
    return props.history.push('/')
  }

  return (
    <div className='column center middle max-h'>
      <div className='shadow-box col col-3'>
        <h1>Redirect&nbsp;to&nbsp;Abyss&nbsp;page</h1>
        <div className='row center justify m-2'>
          <NavLink
            to={
              '/auth/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiMDc0OC1hY2M1LTRjMDgtZjIyOSIsIm5pY2tuYW1lIjoibG9sIiwidGFnIjoiNzQzNiIsImxhbmciOiJydSIsInRpbWVzdGFtcCI6MTYwODk0Mzc5Ny41MDgyMDh9.7UcMMkaiJBkFFAnuGXYB1_0C_NxgDCv2K7NyKHMT8PQ'
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
