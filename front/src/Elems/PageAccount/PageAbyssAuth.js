import React, { useContext, useEffect, useState } from "react"
import { Redirect, useParams } from "react-router-dom"
import AppContext from "../../context/application/appContext"
import Loader from "../AppComponents/Loader"

const PageAbyssAuth = (props) => {
  const { accLogin, accLogout } = useContext(AppContext)
  const [authed, setAuthed] = useState(false)
  const [noAccess, setNoAccess] = useState(false)
  const { key } = useParams()

  useEffect(() => {
    accLogout()
    if (key)
      accLogin({ key: key }).then((authStatus) => {
        if (authStatus) setAuthed(true)
        else setNoAccess(true)
      })
    // eslint-disable-next-line
  }, [key])

  // const q = props.location.search
  // const params = new URLSearchParams(q)
  // const abySecID = params.get("key")

  if (noAccess) return <Redirect from='*' to={`/login`} />
  if (authed) return <Redirect from='*' to={`/`} />
  return (
    <div>
      <h1>Проверка аккаунта</h1>
      <Loader />
    </div>
  )

  // if (prjID) return <Redirect from='*' to={`/prj/${prjID}`} />
  // return <Redirect from='*' to='/' />
}

export default PageAbyssAuth
