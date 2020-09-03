import React, { useContext, useEffect } from "react"
import { Redirect } from "react-router-dom"

import AppContext from "../../context/application/appContext"
import { DisplayImage } from "../images"

const PageTranslateRoot = (props) => {
  const { translates } = useContext(AppContext)

  useEffect(() => {
    let redirectTimer = setTimeout(() => props.history.push("/"), 1500)
    return () => {
      clearTimeout(redirectTimer)
    }
    // eslint-disable-next-line
  }, [])

  if (translates.id) return <Redirect to={`translates/${translates.id}`} />

  return (
    <div className='container-fluid'>
      <div className='row justify center m-3'>
        <div className='row center'>
          <div className='card card-image-small mb-1'>
            <DisplayImage name='extensions' />
          </div>
          <h1 className='t-big ph-2'>Файл не выбран</h1>
        </div>
      </div>
      <hr />
      <div className='m-3'>&nbsp;</div>
    </div>
  )
}

export default PageTranslateRoot
