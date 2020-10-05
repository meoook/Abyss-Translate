import React, { useContext } from "react"
import { Redirect } from "react-router-dom"
import AppContext from "../../context/application/appContext"

const PageOAuthCB = (props) => {
  const { repoAccess } = useContext(AppContext)

  const q = props.location.search
  const params = new URLSearchParams(q)
  const error_description = params.get("error_description")
  const code_param = params.get("code")

  const folderID = localStorage.getItem("oauth_callback_folder")
  const prjID = localStorage.getItem("oauth_callback_save_id")
  localStorage.removeItem("oauth_callback_folder")
  localStorage.removeItem("oauth_callback_save_id")

  if (prjID && folderID && code_param) repoAccess(prjID, folderID, "oauth", code_param)
  else console.log(error_description)

  if (prjID) return <Redirect from='*' to={`/prj/${prjID}`} />
  return <Redirect from='*' to='/' />
}

export default PageOAuthCB
